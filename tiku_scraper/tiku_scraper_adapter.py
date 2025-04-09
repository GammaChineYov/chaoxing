from api.answer import Tiku
from tiku_scraper.single_scrape_session import SingleScrapeSession
from api.logger import logger




class TikuScraperAdapter(Tiku):
    """
    Tiku adapter using SingleScrapeSession while preserving original logic.
    """
    def __init__(self) -> None:
        super().__init__()
        self.name = 'ScraperTikuAdapter'
        self.scraper = SingleScrapeSession()  # Use single thread version

    def _filter_results(self, raw_results):
            """
            Filter raw results to keep only those with A/B/C/D in answer.
            
            Args:
                raw_results (list): List of raw result dicts from ScrapeSession
                
            Returns:
                list: Filtered results containing only valid answers
            """
            if not raw_results:
                return []
                
            filtered = []
            for result in raw_results:
                answer = result.get('answer', '')
                if any(marker in answer for marker in ['A', 'B', 'C', 'D']):
                    filtered.append(result)
                    
            return filtered

    def _extract_options_from_question(self, question_text):
        """Extract options from question text with precise pattern matching"""
        import re
        # Match options starting with A. B. C. D. (with either . or ．)
        option_pattern = re.compile(r'[A-D][．.]')
        options = option_pattern.split(question_text)
        if not options or len(options) <2:
            return None
        return [opt.strip() for opt in options[1:] if opt.strip()]

    def _sort_results_by_similarity(self, results, query_text):
        """Sort results by similarity to query text using difflib"""
        import difflib
        return sorted(
            results,
            key=lambda x: difflib.SequenceMatcher(
                None,
                x['question'] + x.get('answer', ''),
                query_text
            ).ratio(),
            reverse=True
        )

    def _query(self, q_info: dict):
        """
        Query implementation with filtering and similarity sorting.
        
        Args:
            q_info (dict): Question information
            
        Returns:
            str: Best matched options based on similarity and answer markers
        """
        if q_info['type'] not in ['single', 'multiple']:
            logger.warning(f"Unsupported question type: {q_info['type']}")
            return None

        try:
            # Get and filter results
            raw_results = self.scraper.scrape_question(q_info['title'])
            filtered_results = self._filter_results(raw_results)
            if not filtered_results:
                return None

            # Sort by similarity to original question
            query_text = q_info['title'] + ' '.join(q_info.get('options', []))
            sorted_results = self._sort_results_by_similarity(filtered_results, query_text)
            best_match = sorted_results[0]
            answer_text = best_match['answer']
            question_text = best_match['question']

            # Extract options from question text
            options = self._extract_options_from_question(question_text)
            if not options:
                return None

            # Match options based on answer markers
            matched_options = []
            for i in range(min(len(options), 4)):  # Only check A-D
                if chr(65 + i) in answer_text:  # 65 is ASCII for 'A'
                    matched_options.append(options[i])

            return '\n'.join(matched_options) if matched_options else None

        except Exception as e:
            logger.error(f"Error in ScraperTiku query: {e}")
            return None

    def __del__(self):
        """Clean up resources when object is destroyed"""
        if hasattr(self, 'scraper') and self.scraper:
            del self.scraper
        super().__del__()

if __name__ == '__main__':
    # Test the ScraperTiku with an example question
    tiku = TikuScraperAdapter()
    
    # Example question data
    question = {
        'type': 'single',
        'title': '计算机的主机由CPU和( )组成。',
        'options': ['A.内存', 'B.外存', 'C.硬盘', 'D.显示器']
    }
    
    # Query the answer
    result = tiku._query(question)
    print(f"Question: {question['title']}")
    print(f"Options: {question['options']}")
    print(f"Answer: {result}")

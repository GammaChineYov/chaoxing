#!/usr/bin/env python3
import argparse
import json
from scrape_session import ScrapeSession

def interactive_mode(scraper):
    """Interactive command line interface"""
    print("Interactive Question Scraper")
    print("Type your questions (or 'quit' to exit)")
    
    while True:
        try:
            question = input("> ").strip()
            if not question:
                continue
            if question.lower() in ('quit', 'exit'):
                break
                
            results = scraper.scrape_question(question)
            if not results:
                print("No results found")
                continue
                
            print("\nResults:")
            for i, item in enumerate(results, 1):
                print(f"{i}. Question: {item['question']}")
                print(f"   Answer: {item['answer']}\n")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            import traceback
            error_msg = f"Error at line {traceback.extract_tb(e.__traceback__)[-1].lineno}: {str(e)}"
            print(error_msg)
            print(f"Full traceback:\n{''.join(traceback.format_tb(e.__traceback__))}")

def main():
    parser = argparse.ArgumentParser(description='Question scraper CLI tool')
    parser.add_argument('-q', '--question', help='Single question text to scrape')
    parser.add_argument('-f', '--file', help='File containing questions (one per line)')
    parser.add_argument('-o', '--output', help='Output file path for results')
    parser.add_argument('-i', '--interactive', action='store_true', help='Run in interactive mode')
    args = parser.parse_args()

    scraper = ScrapeSession()

    if args.interactive:
        interactive_mode(scraper)
        return

    results = []
    if args.question:
        results = scraper.scrape_question(args.question)
    elif args.file:
        with open(args.file, 'r') as f:
            questions = [line.strip() for line in f if line.strip()]
            for question in questions:
                results.extend(scraper.scrape_question(question))

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    elif results:
        print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

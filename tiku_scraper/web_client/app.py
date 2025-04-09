#!/usr/bin/env python3
import sys
sys.path.append("../")
from flask import Flask, render_template, request, jsonify
from scrape_session import ScrapeSession
import traceback
from loguru import logger

logger.add("web_client.log", rotation="10 MB", level="TRACE")


app = Flask(__name__)
scraper = ScrapeSession()

@app.route('/')
def index():    
    """Render main page"""
    return render_template('index.html')

@app.route('/api/scrape', methods=['GET', 'POST'])
def scrape_question():
    """API endpoint for question scraping"""
    from datetime import datetime
    
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'endpoint': '/api/scrape',
        'method': request.method
    }
    
    try:
        # Get question from request
        if request.method == 'GET':
            question = request.args.get('q')
        else:
            data = request.get_json() or {}
            question = data.get('question')
        
        if not question:
            app.logger.error("Question is required")
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': 'Question is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        question = question.strip()
        log_data['question'] = question
        
        # Perform scraping
        results = scraper.scrape_question(question)
        log_data['result_count'] = len(results)
        
        if not results:
            app.logger.info(f"No results found for question: {question}")
        else:
            app.logger.info(f"Found {len(results)} results for question: {question}")
        
        return jsonify({
            **log_data,
            'results': results
        })
        
    except Exception as e:
        app.logger.error(f"{type(e).__name__}: {str(e)}")
        app.logger.trace(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': str(e),
            'error_type': type(e).__name__,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/batch_scrape', methods=['POST'])
def batch_scrape():
    """API endpoint for batch question scraping"""
    from datetime import datetime
    
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'endpoint': '/api/batch_scrape',
        'method': 'POST'
    }
    
    try:
        data = request.get_json() or {}
        log_data['input_questions_count'] = len(data.get('questions', []))
        
        if not data or 'questions' not in data:
            app.logger.error("Questions list is required")
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': 'Questions list is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        questions = [q.strip() for q in data['questions'] if q.strip()]
        if not questions:
            app.logger.error("No valid questions provided")
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': 'No valid questions provided',
                'timestamp': datetime.now().isoformat()
            }), 400
            
        results = []
        processed_questions = []
        
        for question in questions:
            try:
                question_results = scraper.scrape_question(question)
                results.extend(question_results)
                processed_questions.append({
                    'question': question,
                    'result_count': len(question_results)
                })
            except Exception as e:
                processed_questions.append({
                    'question': question,
                    'error': str(e),
                    'error_type': type(e).__name__
                })
                app.logger.error(f"Error processing question '{question}': {type(e).__name__}: {str(e)}")
                app.logger.trace(traceback.format_exc())
        
        log_data.update({
            'status': 'completed',
            'code': 200,
            'total_results': len(results),
            'processed_questions': processed_questions
        })
        app.logger.info(f"Batch processing completed. Total results: {len(results)}, Processed questions: {len(processed_questions)}")
        
        return jsonify({
            **log_data,
            'results': results
        })
        
    except Exception as e:
        app.logger.error(f"{type(e).__name__}: {str(e)}")
        app.logger.trace(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': str(e),
            'error_type': type(e).__name__,
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

def extract_from_url(url: str) -> Dict:
    """Extract text from URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        main = soup.find('main') or soup.find('article') or soup.find('body')
        paragraphs = main.find_all(['p', 'h1', 'h2', 'h3', 'li']) if main else []
        text = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        title = soup.find('title')
        
        return {
            "status": "success", "type": "url", "source": url,
            "title": title.get_text().strip() if title else "Untitled",
            "content": text[:15000], "word_count": len(text.split())
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def extract_from_pdf(pdf_path: str) -> Dict:
    """Extract text from PDF with robust error handling."""
    try:
        # Add validation
        validation = safe_file_read(pdf_path, ['.pdf'])
        if validation["status"] == "error":
            return {"status": "error", "message": validation["error"]}
        
        text = ""
        with open(pdf_path, 'rb') as f:
            try:
                reader = PyPDF2.PdfReader(f)
                num_pages = len(reader.pages)
                
                # Check for empty PDF
                if num_pages == 0:
                    return {"status": "error", "message": "PDF has no pages"}
                
                # Limit to first 50 pages to avoid timeouts
                for i, page in enumerate(reader.pages[:50]):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as page_err:
                        logger.warning(f"Could not extract page {i}: {page_err}")
                        continue
                
                # Check if any text was extracted
                if not text.strip():
                    return {"status": "error", "message": "Could not extract any text from PDF"}
                
                return {
                    "status": "success", 
                    "type": "pdf", 
                    "source": pdf_path,
                    "content": text[:15000], 
                    "word_count": len(text.split()),
                    "pages": min(num_pages, 50)
                }
            except Exception as read_err:
                return {"status": "error", "message": f"PDF reading error: {str(read_err)}"}
                
    except Exception as e:
        logger.error(f"PDF extraction error: {e}\n{traceback.format_exc()}")
        return {"status": "error", "message": f"PDF processing failed: {str(e)}"}


def summarize_content(
    user_id: str,
    text: str = None,
    url: str = None,
    pdf_path: str = None,
    output_format: str = "all"
) -> Dict:
    """
    Enhanced summarizer supporting TEXT, URL, and PDF only.
    
    REMOVED FORMATS: DOCX, IPYNB (not working reliably)
    
    Parameters:
    - user_id: User identifier
    - text: Text to analyze (direct input)
    - url: URL to fetch and summarize
    - pdf_path: Path to PDF file
    - output_format: "summary", "quiz", "findings", "mindmap", "all"
    
    Returns: Comprehensive analysis with AI-generated insights
    """
    start = time.time()
    user = get_user(user_id)
    
    # Extract content from available sources
    extracted = None
    
    if url:
        extracted = extract_from_url(url)
    elif pdf_path:
        extracted = extract_from_pdf(pdf_path)
    elif text and len(text) >= 50:
        extracted = {"status": "success", "type": "text", "content": text, "word_count": len(text.split())}
    else:
        return {
            "status": "needs_input",
            "message": f"📄 {user.name}, I can summarize content in these formats:",
            "supported_formats": [
                "✅ Direct text (paste or type)",
                "✅ URL (any website)",
                "✅ PDF (documents up to 50 pages)"
            ],
            "removed_formats": [
                "❌ DOCX (removed - not working)",
                "❌ IPYNB (removed - not working)"
            ],
            "examples": [
                "Summarize: [paste your text here]",
                "Summarize: https://example.com/article",
                "Upload a PDF file"
            ]
        }
    
    if extracted.get("status") == "error":
        return extracted
    
    content = extracted["content"]
    word_count = extracted.get("word_count", 0)
    
    # Calculate reading time
    reading_time = max(1, word_count // 200)  # Average 200 words per minute
    
    # Use Gemini for AI summarization
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Enhanced prompt for general content
        prompt = f"""Analyze this content comprehensively. Return ONLY valid JSON:
{{
    "summary": "3-4 sentence summary",
    "key_points": ["point1", "point2", "point3", "point4", "point5"],
    "action_items": ["actionable task 1", "actionable task 2"],
    "key_entities": {{
        "people": ["person1", "person2"],
        "organizations": ["org1", "org2"],
        "locations": ["place1", "place2"]
    }},
    "sentiment": "positive/negative/neutral/mixed",
    "main_topics": ["topic1", "topic2", "topic3"],
    "difficulty_level": "easy/moderate/complex",
    "mind_map": {{
        "central_topic": "main topic",
        "branches": ["subtopic1", "subtopic2", "subtopic3"]
    }},
    "quiz": [
        {{"question": "What is the main idea?", "options": ["A) Option", "B) Option", "C) Option", "D) Option"], "answer": "A"}},
        {{"question": "According to the text...", "options": ["A) Option", "B) Option", "C) Option", "D) Option"], "answer": "C"}}
    ],
    "key_findings": ["finding1", "finding2", "finding3"]
}}

Content: {content[:8000]}"""
        
        # Add max_output_tokens to ensure complete JSON
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=2048,
                temperature=0.3
            )
        )
        response_text = response.text.strip()
        
        # Clean JSON from markdown
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]
        
        response_text = response_text.strip()
        
        # Try to parse JSON
        try:
            ai_result = json.loads(response_text)
        except json.JSONDecodeError as je:
            logger.error(f"JSON parsing error: {je}")
            logger.error(f"Response text: {response_text[:500]}")
            raise Exception("Invalid JSON from AI")
        
    except Exception as e:
        logger.error(f"AI summarization failed: {e}")
        # Enhanced fallback
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
        
        ai_result = {
            "summary": '. '.join(sentences[:3]) + '.',
            "key_points": sentences[:5],
            "main_topics": ["General content"],
            "sentiment": "neutral",
            "difficulty_level": "moderate",
            "quiz": [],
            "key_findings": sentences[:3],
            "action_items": [],
            "error_note": "Using fallback analysis"
        }
    
    # Build enhanced result
    result = {
        "status": "complete",
        "source_type": extracted.get("type"),
        "source": extracted.get("source", "text input"),
        "metadata": {
            "word_count": word_count,
            "reading_time": f"{reading_time} min",
            "processing_time": f"{time.time() - start:.2f}s",
            "difficulty": ai_result.get("difficulty_level", "moderate"),
            "sentiment": ai_result.get("sentiment", "neutral")
        }
    }
    
    # Add content based on output_format
    if output_format in ["summary", "all"]:
        result["summary"] = ai_result.get("summary")
        result["key_points"] = ai_result.get("key_points", [])
        result["main_topics"] = ai_result.get("main_topics", [])
    
    if output_format in ["quiz", "all"]:
        result["quiz"] = ai_result.get("quiz", [])
    
    if output_format in ["findings", "all"]:
        result["key_findings"] = ai_result.get("key_findings", [])
    
    if output_format in ["mindmap", "all"]:
        result["mind_map"] = ai_result.get("mind_map", {})
    
    if output_format in ["all"]:
        result["action_items"] = ai_result.get("action_items", [])
        result["key_entities"] = ai_result.get("key_entities", {})
    
    # Update user stats
    user.total_points += 30
    
    # Award badges for document processing
    docs_processed = user_journeys[user_id].game_scores.get("docs_processed", 0) + 1
    user_journeys[user_id].game_scores["docs_processed"] = docs_processed
    
    if docs_processed == 5 and "📚 Knowledge Seeker" not in user.badges:
        user.badges.append("📚 Knowledge Seeker")
        result["new_badge"] = "📚 Knowledge Seeker"
    elif docs_processed == 20 and "📚📚 Research Master" not in user.badges:
        user.badges.append("📚📚 Research Master")
        result["new_badge"] = "📚📚 Research Master"
    
    metric_inc("summaries")
    metric_time("summarizer", time.time() - start)
    
    result["stats"] = {
        "points_earned": 30,
        "total_points": user.total_points,
        "documents_processed": docs_processed
    }
    
    return result

print("✅ Agent 7: Summarizer (Text/URL/PDF only) ready")

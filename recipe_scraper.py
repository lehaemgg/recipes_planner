import requests
from bs4 import BeautifulSoup
import re
import json

def scrape_menunedeli_recipe(url):
    """
    Scrape recipe data from menunedeli.ru
    Returns dict with title, ingredients, and steps
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_elem = soup.find('h1') or soup.find('title')
        title = title_elem.get_text().strip() if title_elem else "Imported Recipe"
        
        # Extract ingredients
        ingredients = []
        portions = 1  # Default to 1 portion
        
        # Look for portion information in various formats
        portion_text = soup.get_text()
        portion_patterns = [
            r'На кол-во порций[:\s]*([0-9]+)',
            r'порций[:\s]*([0-9]+)',
            r'([0-9]+)\s*порци',
            r'([0-9]+)\s*человек'
        ]
        
        for pattern in portion_patterns:
            portion_match = re.search(pattern, portion_text, re.IGNORECASE)
            if portion_match:
                portions = int(portion_match.group(1))
                break
        
        # Default to 4 portions for menunedeli.ru if not found
        if portions == 1:
            portions = 4
        
        # Try different selectors for ingredients
        ingredient_selectors = [
            '.recipe-ingredients li',
            '.ingredients li',
            '[class*="ingredient"] li',
            '.recipe-content ul li'
        ]
        
        for selector in ingredient_selectors:
            ingredient_elements = soup.select(selector)
            if ingredient_elements:
                for elem in ingredient_elements:
                    text = elem.get_text().strip()
                    if text and len(text) > 2:  # Filter out empty or very short items
                        # Parse quantity, unit, and name from Russian text
                        # Look for patterns like "Рис – 200 г" or "Голень куриная – 900 г"
                        if '–' in text or '-' in text:
                            parts = re.split(r'[–-]', text, 1)
                            if len(parts) == 2:
                                name = parts[0].strip()
                                amount_text = parts[1].strip()
                                
                                # Extract quantity and unit from amount text
                                amount_match = re.match(r'(\d+(?:[.,]\d+)?)\s*([а-яё\w.]*)', amount_text)
                                if amount_match:
                                    quantity = round(float(amount_match.group(1).replace(',', '.')) / portions, 2)
                                    unit = amount_match.group(2) or 'шт'
                                else:
                                    quantity = round(1.0 / portions, 2)
                                    unit = amount_text if amount_text else 'шт'
                            else:
                                name = text
                                quantity = 1.0
                                unit = 'шт'
                        else:
                            # Fallback parsing
                            match = re.match(r'^(.+?)\s+(\d+(?:[.,]\d+)?)\s*([а-яё\w.]*)$', text)
                            if match:
                                name = match.group(1)
                                quantity = round(float(match.group(2).replace(',', '.')) / portions, 2)
                                unit = match.group(3) or 'шт'
                            else:
                                name = text
                                quantity = round(1.0 / portions, 2)
                                unit = 'шт'
                        
                        ingredients.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit
                        })
                break
        
        # Extract steps
        steps = []
        
        # Try different selectors for detailed steps (not short summary)
        step_selectors = [
            '.recipe-steps li',
            '.recipe-method li', 
            '.detailed-steps li',
            '.full-recipe li',
            'div[class*="step"] p',
            '.recipe-instruction p',
            '.cooking-method p'
        ]
        
        for selector in step_selectors:
            step_elements = soup.select(selector)
            if step_elements:
                for i, elem in enumerate(step_elements, 1):
                    text = elem.get_text().strip()
                    if text and len(text) > 10:  # Filter out very short steps
                        steps.append({
                            'order': i,
                            'description': text
                        })
                break
        
        # If no structured steps found, look for step markers
        if not steps:
            all_text = soup.get_text()
            
            # Split by step markers like "Шаг 1", "Шаг 2", etc.
            step_pattern = r'Шаг\s+(\d+)([\s\S]*?)(?=Шаг\s+\d+|Категории:|$)'
            step_matches = re.findall(step_pattern, all_text, re.IGNORECASE)
            
            for step_num, step_content in step_matches:
                # Clean up the step content and stop at "Категории:"
                step_text = re.sub(r'\s+', ' ', step_content.strip())
                # Remove everything after "Категории:"
                if 'Категории:' in step_text:
                    step_text = step_text.split('Категории:')[0].strip()
                
                # Extract step photo
                step_photo_url = None
                step_section = soup.find(string=re.compile(f'Шаг\\s+{step_num}', re.IGNORECASE))
                if step_section:
                    # Look for images near this step
                    parent = step_section.parent
                    for _ in range(5):  # Search up to 5 parent levels
                        if parent:
                            img = parent.find('img')
                            if img and img.get('src'):
                                img_src = img.get('src')
                                if img_src.startswith('/'):
                                    step_photo_url = 'https://menunedeli.ru' + img_src
                                elif img_src.startswith('http'):
                                    step_photo_url = img_src
                                break
                            parent = parent.parent
                        else:
                            break
                
                if len(step_text) > 20:
                    step_data = {
                        'order': int(step_num),
                        'description': step_text
                    }
                    if step_photo_url:
                        # Download image and encode as base64
                        try:
                            img_response = requests.get(step_photo_url, headers=headers, timeout=10)
                            if img_response.status_code == 200:
                                import base64
                                from PIL import Image
                                from io import BytesIO
                                
                                # Resize image before encoding
                                img = Image.open(BytesIO(img_response.content))
                                if img.height > 800 or img.width > 800:
                                    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                                
                                buffer = BytesIO()
                                img.save(buffer, format='JPEG', optimize=True, quality=85)
                                image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                                step_data['photo_data'] = image_data
                                step_data['photo_url'] = step_photo_url
                        except Exception as e:
                            print(f"Failed to download image {step_photo_url}: {e}")
                    steps.append(step_data)
        
        return {
            'success': True,
            'title': title,
            'ingredients': ingredients,
            'steps': steps
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    # Test with the provided URL
    url = "https://menunedeli.ru/recipe/kurinye-nozhki-v-duxovke-s-risom/"
    result = scrape_menunedeli_recipe(url)
    
    # Handle encoding for Windows console
    import sys
    if sys.platform == 'win32':
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
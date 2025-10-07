import os
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image
import PyPDF2
import docx
import mimetypes
from io import BytesIO

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

class DocumentProcessor:
    """Handles multimodal document processing - PDFs, images, text files"""

    def __init__(self):
        self.supported_formats = {
            'pdf': self._process_pdf,
            'txt': self._process_text,
            'docx': self._process_docx,
            'jpg': self._process_image,
            'jpeg': self._process_image,
            'png': self._process_image,
            'gif': self._process_image,
            'bmp': self._process_image,
            'webp': self._process_image
        }

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process any supported file and return structured content"""

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Detect file type
        file_extension = file_path.suffix.lower().lstrip('.')
        mime_type, _ = mimetypes.guess_type(str(file_path))

        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")

        # Process file
        processor = self.supported_formats[file_extension]
        content = processor(file_path)

        # Add metadata
        content.update({
            'filename': file_path.name,
            'file_path': str(file_path),
            'file_type': file_extension,
            'mime_type': mime_type,
            'file_size': file_path.stat().st_size
        })

        return content

    def _process_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract text and images from PDF with fallback options"""

        # Try pdfplumber first (more robust)
        if PDFPLUMBER_AVAILABLE:
            try:
                return self._process_pdf_with_pdfplumber(file_path)
            except Exception as e:
                print(f"pdfplumber failed: {e}, trying PyPDF2...")

        # Fallback to PyPDF2
        return self._process_pdf_with_pypdf2(file_path)

    def _process_pdf_with_pdfplumber(self, file_path: Path) -> Dict[str, Any]:
        """Process PDF using pdfplumber (more reliable)"""
        content = {
            'type': 'pdf',
            'pages': [],
            'text': '',
            'images': []
        }

        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text() or f"[Page {page_num + 1} - no text found]"

                        content['pages'].append({
                            'page_number': page_num + 1,
                            'text': page_text
                        })
                        content['text'] += f"\\n\\n--- Page {page_num + 1} ---\\n{page_text}"

                        # Extract images using pdfplumber
                        if hasattr(page, 'images') and page.images:
                            for img_idx, img in enumerate(page.images):
                                content['images'].append({
                                    'page': page_num + 1,
                                    'type': 'embedded_image',
                                    'description': f"Image {img_idx + 1} from page {page_num + 1}"
                                })

                    except Exception as page_error:
                        error_text = f"[Page {page_num + 1} processing failed: {str(page_error)}]"
                        content['pages'].append({
                            'page_number': page_num + 1,
                            'text': error_text
                        })
                        content['text'] += f"\\n\\n--- Page {page_num + 1} ---\\n{error_text}"

        except Exception as e:
            content['error'] = f"Failed to process PDF with pdfplumber: {str(e)}"

        return content

    def _process_pdf_with_pypdf2(self, file_path: Path) -> Dict[str, Any]:
        """Process PDF using PyPDF2 (fallback)"""
        content = {
            'type': 'pdf',
            'pages': [],
            'text': '',
            'images': []
        }

        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)

                for page_num, page in enumerate(reader.pages):
                    try:
                        # Extract text safely
                        page_text = page.extract_text()
                        if not page_text:
                            page_text = f"[Page {page_num + 1} - text extraction failed]"

                        content['pages'].append({
                            'page_number': page_num + 1,
                            'text': page_text
                        })
                        content['text'] += f"\\n\\n--- Page {page_num + 1} ---\\n{page_text}"

                        # Safely extract images
                        try:
                            self._extract_pdf_images_safe(page, page_num + 1, content)
                        except Exception as img_error:
                            # Log but don't fail the whole process
                            content['images'].append({
                                'page': page_num + 1,
                                'type': 'extraction_failed',
                                'description': f"Image extraction failed on page {page_num + 1}"
                            })

                    except Exception as page_error:
                        # If a page fails, continue with others
                        error_text = f"[Page {page_num + 1} processing failed: {str(page_error)}]"
                        content['pages'].append({
                            'page_number': page_num + 1,
                            'text': error_text
                        })
                        content['text'] += f"\\n\\n--- Page {page_num + 1} ---\\n{error_text}"

        except Exception as e:
            content['error'] = f"Failed to process PDF with PyPDF2: {str(e)}"

        return content

    def _extract_pdf_images_safe(self, page, page_num: int, content: Dict[str, Any]):
        """Safely extract images from PDF page"""
        try:
            # Get resources safely
            resources = page.get('/Resources')
            if not resources:
                return

            # Check if resources is an IndirectObject and resolve it
            if hasattr(resources, 'get_object'):
                resources = resources.get_object()

            # Ensure resources is a dictionary-like object
            if not hasattr(resources, 'get'):
                return

            # Get XObject safely
            xobject = resources.get('/XObject')
            if not xobject:
                return

            # Check if xobject is an IndirectObject and resolve it
            if hasattr(xobject, 'get_object'):
                xobject = xobject.get_object()

            # Ensure xobject is iterable and has keys
            if not hasattr(xobject, 'keys') or not callable(getattr(xobject, 'keys', None)):
                return

            # Now safely iterate through objects
            try:
                obj_names = list(xobject.keys())
            except (TypeError, AttributeError):
                return

            for obj_name in obj_names:
                try:
                    obj = xobject[obj_name]

                    # Resolve IndirectObject if needed
                    if hasattr(obj, 'get_object'):
                        obj = obj.get_object()

                    # Check if it's an image - ensure obj has get method
                    if (hasattr(obj, 'get') and callable(getattr(obj, 'get', None)) and
                        obj.get('/Subtype') == '/Image'):

                        content['images'].append({
                            'page': page_num,
                            'type': 'embedded_image',
                            'description': f"Image from page {page_num}",
                            'object_name': str(obj_name)
                        })
                except Exception:
                    # Skip problematic individual objects
                    continue

        except Exception:
            # If anything fails, just skip image extraction for this page
            pass

    def _process_text(self, file_path: Path) -> Dict[str, Any]:
        """Process plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()

            return {
                'type': 'text',
                'text': text,
                'word_count': len(text.split()),
                'line_count': len(text.split('\\n'))
            }
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    text = file.read()
                return {
                    'type': 'text',
                    'text': text,
                    'encoding': 'latin-1',
                    'word_count': len(text.split())
                }
            except Exception as e:
                return {
                    'type': 'text',
                    'error': f"Failed to read text file: {str(e)}"
                }

    def _process_docx(self, file_path: Path) -> Dict[str, Any]:
        """Process Word documents"""
        try:
            doc = docx.Document(file_path)

            paragraphs = []
            full_text = ""

            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)
                    full_text += para.text + "\\n"

            return {
                'type': 'docx',
                'text': full_text,
                'paragraphs': paragraphs,
                'paragraph_count': len(paragraphs),
                'word_count': len(full_text.split())
            }

        except Exception as e:
            return {
                'type': 'docx',
                'error': f"Failed to process DOCX: {str(e)}"
            }

    def _process_image(self, file_path: Path) -> Dict[str, Any]:
        """Process image files"""
        try:
            with Image.open(file_path) as img:
                # Convert to base64 for vision model
                buffer = BytesIO()
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(buffer, format='JPEG', quality=85)
                image_base64 = base64.b64encode(buffer.getvalue()).decode()

                return {
                    'type': 'image',
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'base64': image_base64,
                    'size_bytes': len(buffer.getvalue()),
                    'description': f"{img.format} image ({img.width}x{img.height})"
                }

        except Exception as e:
            return {
                'type': 'image',
                'error': f"Failed to process image: {str(e)}"
            }

    def extract_text_content(self, processed_content: Dict[str, Any]) -> str:
        """Extract all text content from processed document"""
        if 'error' in processed_content:
            return f"Error processing file: {processed_content['error']}"

        content_type = processed_content.get('type', '')

        if content_type in ['text', 'pdf', 'docx']:
            return processed_content.get('text', '')
        elif content_type == 'image':
            return processed_content.get('description', 'Image file')
        else:
            return f"Unknown content type: {content_type}"

    def get_images_for_vision(self, processed_content: Dict[str, Any]) -> List[str]:
        """Extract base64 images for vision model processing"""
        images = []

        content_type = processed_content.get('type', '')

        if content_type == 'image' and 'base64' in processed_content:
            images.append(processed_content['base64'])
        elif content_type == 'pdf' and 'images' in processed_content:
            # For PDF images, we'd need more complex extraction
            # For now, return empty list
            pass

        return images
import PyPDF2
from docx import Document
from docx.opc.exceptions import PackageNotFoundError


# 读取文本文件
def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        return "文件未找到"
    except Exception as e:
        return str(e)


# 读取PDF文件
def read_pdf_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfFileReader(file)
            text = ""
            for page_num in range(pdf_reader.numPages):
                page = pdf_reader.getPage(page_num)
                text += page.extract_text()
            return text
    except FileNotFoundError:
        return "文件未找到"
    except Exception as e:
        return str(e)


def read_docx(file_path):
    try:
        # 加载文档
        document = Document(file_path)
        text = ""
        # 遍历文档中的每个段落并收集文本
        for para in document.paragraphs:
            text += para.text + '\n'
        return text
    except PackageNotFoundError:
        return "文件未找到或不是有效的.docx文件。"
    except Exception as e:
        # 返回异常的字符串描述
        return f"发生错误: {str(e)}"


def read_file(file_path, file_type):
    if file_type == "pdf":
        return read_pdf_file(file_path)
    elif file_type == "txt":
        return read_text_file(file_path)
    elif file_type == "docx":
        return read_docx(file_path)


if __name__ == "__main__":
    # 使用示例
    text_content = read_text_file('example.txt')
    print(text_content)
    pdf_content = read_pdf_file('example.pdf')
    print(pdf_content)

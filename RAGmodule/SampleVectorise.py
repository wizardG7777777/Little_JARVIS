from pathlib import Path
from RAG import RagUniversal
from langchain.text_splitter import MarkdownTextSplitter, MarkdownHeaderTextSplitter


def process_markdown_with_langchain(markdown_file_path):
    # The langchain in-built markdown splitter does not work well with the real markdown
    with open(markdown_file_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    # Create markdown splitter
    markdown_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=100)

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(markdown_content)
    """
        The return value is a list, each elements is a Document object
        [
            metadata = {
                "Header X": "Header X content"
            },
            page_content = "text content of Header X"
        ]
    """
    return md_header_splits


def split_markdown_semantic(file_path):
    """
    This markdown splitter works well with the real markdown file
    Split a markdown file into semantic blocks.

    Args:
        file_path (str): Path to the markdown file

    Returns:
        list: List of strings, each representing a semantic block
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    blocks = []
    current_block = ""
    in_code_block = False
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Handle code blocks as complete units
        if line.strip().startswith('```'):
            if not in_code_block:
                # Start of a new code block
                if current_block.strip():
                    blocks.append(current_block.strip())
                current_block = line + '\n'
                in_code_block = True
            else:
                # End of a code block
                current_block += line + '\n'
                blocks.append(current_block.strip())
                current_block = ""
                in_code_block = False
            i += 1
            continue

        if in_code_block:
            current_block += line + '\n'
            i += 1
            continue

        # Headers start new blocks
        if line.strip().startswith('#'):
            if current_block.strip():
                blocks.append(current_block.strip())
            current_block = line + '\n'
            i += 1
            continue

        # Empty lines separate paragraphs
        if not line.strip():
            if current_block.strip():
                blocks.append(current_block.strip())
                current_block = ""
            i += 1
            continue

        # Handle list items
        if (line.strip().startswith(('- ', '* ', '+ ')) or
                (line.strip() and line.strip()[0].isdigit() and '.' in line.strip()[:3])):
            # Check if we need to start a new block
            if current_block.strip() and not any(current_block.strip().endswith('\n' + prefix)
                                                 for prefix in ['- ', '* ', '+ ']) and not (
                    current_block.strip().split('\n')[-1].strip() and
                    current_block.strip().split('\n')[-1].strip()[0].isdigit() and
                    '.' in current_block.strip().split('\n')[-1].strip()[:3]):
                blocks.append(current_block.strip())
                current_block = ""

        # Handle blockquotes
        if line.strip().startswith('>'):
            if current_block.strip() and not current_block.strip().split('\n')[-1].startswith('>'):
                blocks.append(current_block.strip())
                current_block = ""

        # Add the current line to the block
        current_block += line + '\n'
        i += 1

    # Add the last block if not empty
    if current_block.strip():
        blocks.append(current_block.strip())

    return blocks


if "__main__" == "__main__":
    # markdown_file_path = str(Path(__file__).resolve().parent.parent / "ExtendMaterial" /"Intruductions" /"CarIntroductions.md")
    # chunks = split_markdown_semantic(markdown_file_path)
    # for chunk in chunks:
    #     print(chunk)
    #     print("-" * 70)
    rag = RagUniversal()
    # rag.add("Default", chunks, {"source": "CarIntroduction"})
    result = rag.retrieve(
        collection_name="Default",
        query="车辆视觉方案",
        n_results=3,
        metadata={"source": "CarIntroduction"}
    )
    for s in result["documents"][0]:
        print(s)
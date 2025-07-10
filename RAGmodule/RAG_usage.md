# RAG.py 使用说明
## 简介
RAG.py 是一个增强检索类的原型程序，其拥有Markdown文件切分，文件向量化并输入到向量数据库，以及根据用户问题进行检索的功能。
### Markdown切分函数
**函数调用**: split_markdown_semantic(self,file_path:str)->List[str]
这是一个Markdown文件切分函数，其会将Markdown文件切分成多个小块，每个小块代表一个语义块。
### VectorDB添加方法
**函数调用**: add(self, documents_text: List[str], collection_name: str = "Default",meta_datas: Optional[Union[List[Dict[str, str]], Dict[str, str]]] = None)
这是一个向量数据库添加数据的函数，可以将documents_text中的文本向量化并添加到向量数据库中。
### VectorDB检索方法
**函数调用**:  retrieve(self, collection_name: str, query: str, n_results: int = 5, metadata: Dict[str, str] = None):
检索和query最相近的前n_results个字段，并返回这些字段的文本内容（或许？我不是很确定这个版本的chromadb的返回数据格式）。
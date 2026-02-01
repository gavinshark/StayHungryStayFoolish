"""
Document Processor Module

Handles document loading and text chunking using LangChain.
Implements Requirements 1.1, 1.2, 1.4, 1.5.
"""

import os
from typing import Optional

from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class DocumentProcessor:
    """
    文档处理器，封装 LangChain 文档加载和分块功能
    
    Attributes:
        chunk_size: 每个块的最大字符数
        chunk_overlap: 块之间的重叠字符数
        text_splitter: LangChain 文本分割器实例
    """
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        初始化文档处理器
        
        Args:
            chunk_size: 每个块的最大字符数，默认 500
            chunk_overlap: 块之间的重叠字符数，默认 50
            
        Raises:
            ValueError: 如果 chunk_size <= 0 或 chunk_overlap < 0 或 chunk_overlap >= chunk_size
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be non-negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def load_file(self, file_path: str) -> list[Document]:
        """
        加载单个文档并分块
        
        使用 LangChain TextLoader 加载文档，然后使用 RecursiveCharacterTextSplitter
        进行文本分块。支持 TXT 和 Markdown 格式。
        
        Args:
            file_path: 文档路径
            
        Returns:
            LangChain Document 对象列表，每个对象包含一个文本块
            
        Raises:
            FileNotFoundError: 如果文件路径不存在
            PermissionError: 如果没有读取权限
            UnicodeDecodeError: 如果文件编码无法解析
            
        Validates:
            - Requirement 1.1: 读取文档内容并返回文本数据
            - Requirement 1.2: 正确解析 TXT 或 Markdown 文档内容
            - Requirement 1.4: 将文档切分为指定大小的文本块
            - Requirement 1.5: 保留块之间的重叠以保持上下文连贯性
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 检查是否是文件
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Path is not a file: {file_path}")
        
        # 使用 TextLoader 加载文档
        # TextLoader 支持 TXT 和 Markdown 格式
        loader = TextLoader(file_path, encoding='utf-8')
        
        try:
            documents = loader.load()
        except UnicodeDecodeError:
            # 尝试使用其他编码
            for encoding in ['gbk', 'gb2312', 'latin-1']:
                try:
                    loader = TextLoader(file_path, encoding=encoding)
                    documents = loader.load()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise UnicodeDecodeError(
                    'utf-8', b'', 0, 1,
                    f"Unable to decode file {file_path} with any supported encoding"
                )
        
        # 使用 text_splitter 进行分块
        # 这满足 Requirement 1.4 和 1.5
        chunks = self.text_splitter.split_documents(documents)
        
        return chunks
    
    def load_directory(self, dir_path: str, glob: str = "**/*.txt") -> list[Document]:
        """
        加载目录下所有文档并分块
        
        使用 LangChain DirectoryLoader 递归加载目录下匹配的文档，
        然后使用 RecursiveCharacterTextSplitter 进行文本分块。
        
        Args:
            dir_path: 目录路径
            glob: 文件匹配模式，默认 "**/*.txt" 匹配所有 txt 文件
                  可以使用 "**/*.md" 匹配 Markdown 文件
                  或 "**/*.*" 匹配所有文件
            
        Returns:
            LangChain Document 对象列表，每个对象包含一个文本块
            
        Raises:
            FileNotFoundError: 如果目录路径不存在
            PermissionError: 如果没有读取权限
            
        Validates:
            - Requirement 1.1: 读取文档内容并返回文本数据
            - Requirement 1.2: 正确解析 TXT 或 Markdown 文档内容
            - Requirement 1.4: 将文档切分为指定大小的文本块
            - Requirement 1.5: 保留块之间的重叠以保持上下文连贯性
        """
        # 检查目录是否存在
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        
        # 检查是否是目录
        if not os.path.isdir(dir_path):
            raise FileNotFoundError(f"Path is not a directory: {dir_path}")
        
        # 使用 DirectoryLoader 加载目录下的文档
        # 使用 TextLoader 作为加载器类，支持 TXT 和 Markdown
        loader = DirectoryLoader(
            dir_path,
            glob=glob,
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'},
            show_progress=False,
            use_multithreading=False
        )
        
        try:
            documents = loader.load()
        except Exception as e:
            # 如果加载失败，可能是编码问题，尝试其他编码
            if "codec" in str(e).lower() or "decode" in str(e).lower():
                for encoding in ['gbk', 'gb2312', 'latin-1']:
                    try:
                        loader = DirectoryLoader(
                            dir_path,
                            glob=glob,
                            loader_cls=TextLoader,
                            loader_kwargs={'encoding': encoding},
                            show_progress=False,
                            use_multithreading=False
                        )
                        documents = loader.load()
                        break
                    except Exception:
                        continue
                else:
                    raise
            else:
                raise
        
        # 使用 text_splitter 进行分块
        chunks = self.text_splitter.split_documents(documents)
        
        return chunks

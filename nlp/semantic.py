from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from utils.read_doc import read_docx
from data.data import Message
import thulac


class SemanticSimilarityTool:
    def __init__(self):
        """
        初始化工具类。
        :param documents: 知识库中的文档列表。
        """
        self.vectorizer = TfidfVectorizer()
        self.threshold = 0.2
        self.seg = thulac.thulac(seg_only=False)  # 使用THULAC进行分词和词性标注

    def find_similar_documents(self, message: Message, documents: str):
        words = self.seg.cut(message.content)
        n_words = [w for w, pos in words if pos == 'n' or pos == 'a']
        core_content = []
        for w in n_words:
            core_content += self.__find_similar_documents__(msg=w, documents=documents)
        core_content += self.__find_similar_documents__(msg=message.content, documents=documents)
        core_content = [c[0] for c in core_content if c]
        core_content = set(core_content)
        return "\n".join(core_content)

    def __find_similar_documents__(self, msg: str, documents: list):
        """
        根据给定的阈值找出所有与查询语义相似的文档。
        :param query: 用户的查询字符串。
        :param documents: 匹配的目标文档。
        :return: 一个列表，包含所有相似度高于阈值的文档和它们的相似度。
        """
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        msg_tfidf = self.vectorizer.transform([msg])
        cosine_similarities = cosine_similarity(msg_tfidf, tfidf_matrix).flatten()

        # 获取所有高于阈值的文档索引和相似度
        similar_documents_indices = np.where(cosine_similarities >= self.threshold)[0]
        similar_documents = [(documents[i], cosine_similarities[i]) for i in similar_documents_indices]

        # 按相似度降序排列
        similar_documents.sort(key=lambda x: x[1], reverse=True)

        return similar_documents


semantic_tool = SemanticSimilarityTool()
if __name__ == "__main__":
    docs = read_docx('product_info.docx')
    docs = docs.split("\n")
    print(docs)
    tool = SemanticSimilarityTool()
    query = {"content": "有哪些浴帘杆？"}

    message = Message(**query)
    most_similar_doc = tool.find_similar_documents(message, docs)
    print("最相关的文档是:", most_similar_doc)

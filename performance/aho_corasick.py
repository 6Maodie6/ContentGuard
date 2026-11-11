
from collections import deque


class Node:
    def __init__(self):
        self.children = {}
        self.fail = None
        self.outputs = []


class AhoCorasick:
    def __init__(self, keywords):
        self.root = Node()
        self._build_trie(keywords)
        self._build_failure_links()

    def _build_trie(self, keywords):
        """第一步：把所有关键词插入 Trie。"""
        for keyword in set(keywords):
            node = self.root

            for char in keyword:
                if char not in node.children:
                    node.children[char] = Node()

                node = node.children[char]

            node.outputs.append(keyword)

    def _build_failure_links(self):
        """第二步：使用 BFS 构建 Failure Link。"""
        queue = deque()

        self.root.fail = self.root

        # 根节点的直接子节点，失败时都回到根节点
        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)

        while queue:
            current = queue.popleft()

            for char, child in current.children.items():
                fallback = current.fail

                # 沿 Failure Link 寻找能接收当前字符的节点
                while fallback != self.root and char not in fallback.children:
                    fallback = fallback.fail

                if char in fallback.children:
                    child.fail = fallback.children[char]
                else:
                    child.fail = self.root

                # 继承失败节点的匹配结果
                child.outputs.extend(child.fail.outputs)

                queue.append(child)

    def search(self, text):
        """第三步：扫描文本，返回所有匹配到的关键词。"""
        results = []
        node = self.root

        for index, char in enumerate(text):
            while node != self.root and char not in node.children:
                node = node.fail

            if char in node.children:
                node = node.children[char]
            else:
                node = self.root

            for keyword in node.outputs:
                results.append({
                    "keyword": keyword,
                    "start": index - len(keyword) + 1,
                    "end": index + 1
                })

        return results


if __name__ == "__main__":
    keywords = ["he", "her", "hers", "she"]

    ac = AhoCorasick(keywords)

    text = "shers"
    results = ac.search(text)

    print("原始文本：", text)
    print("匹配结果：")

    for item in results:
        print(item)

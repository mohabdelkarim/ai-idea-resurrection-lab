import random
import math

class Node:
    def __init__(self, score, value, level):
        self.score = score
        self.value = value
        self.next = [None]*level
        self.prev = None

class Skiplist:
    def __init__(self, max_level=16, p=0.5):
        self.max_level = max_level
        self.p = p
        self.level = 1
        self.header = Node(float('-inf'), None, max_level)
        for i in range(max_level):
            self.header.next[i] = None

    def _random_level(self):
        level = 1
        while random.random() < self.p and level < self.max_level:
            level += 1
        return level

    def insert(self, score, value):
        level = self._random_level()
        if level > self.level:
            self.level = level
        node = Node(score, value, level)
        update = [None]*level
        curr = self.header
        for i in range(level-1, -1, -1):
            while curr.next[i] and curr.next[i].score < score:
                curr = curr.next[i]
            update[i] = curr
        for i in range(level):
            node.next[i] = update[i].next[i]
            if update[i].next[i]:
                update[i].next[i].prev = node
            update[i].next[i] = node
            if i == 0:
                node.prev = update[i]

    def delete(self, score, value):
        update = [None]*self.level
        curr = self.header
        for i in range(self.level-1, -1, -1):
            while curr.next[i] and curr.next[i].score < score:
                curr = curr.next[i]
            update[i] = curr
        if curr.next[0] and curr.next[0].score == score and curr.next[0].value == value:
            for i in range(self.level):
                if update[i].next[i] and update[i].next[i].score == score and update[i].next[i].value == value:
                    update[i].next[i] = update[i].next[i].next[i]
                    if update[i].next[i]:
                        update[i].next[i].prev = update[i]
            while self.level > 1 and not self.header.next[self.level-1]:
                self.level -= 1
            return True
        return False

    def zadd(self, score, value):
        update = [None]*self.level
        curr = self.header
        for i in range(self.level-1, -1, -1):
            while curr.next[i] and curr.next[i].score < score:
                curr = curr.next[i]
            update[i] = curr
        if curr.next[0] and curr.next[0].score == score and curr.next[0].value == value:
            return
        node = Node(score, value, self._random_level())
        if node.level > self.level:
            self.level = node.level
        for i in range(node.level):
            node.next[i] = update[i].next[i]
            if update[i].next[i]:
                update[i].next[i].prev = node
            update[i].next[i] = node
            if i == 0:
                node.prev = update[i]

    def zupdate(self, score, value):
        curr = self.header.next[0]
        while curr:
            if curr.score == score and curr.value == value:
                new_score = score + 0.1  # simulate small score delta
                if curr.prev and curr.next[0]:
                    if curr.prev.score < new_score < curr.next[0].score:
                        curr.score = new_score
                        return
                self.delete(score, value)
                self.zadd(new_score, value)
                return
            curr = curr.next[0]

    def print_list(self):
        curr = self.header.next[0]
        while curr:
            print(f"Score: {curr.score}, Value: {curr.value}")
            curr = curr.next[0]

skiplist = Skiplist()
skiplist.insert(10.0, "value1")
skiplist.insert(20.0, "value2")
skiplist.insert(30.0, "value3")
skipped_list.print_list()
skiplist.zupdate(10.0, "value1")
skiplist.print_list()
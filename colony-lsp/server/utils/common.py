from typing import Optional, Tuple, List
from pygls.lsp import types
from pygls.workspace import Document, position_from_utf16

from server.ats.trees.common import YamlNode, Position


class Visitor:
    def __init__(self, cursor_position: types.Position):
        self.found_node = None
        self.cursor_position = Position(line=cursor_position.line, col=cursor_position.character)

    def visit_node(self, node: YamlNode):
        start = Position(node.start_pos[0], node.start_pos[1])
        end = Position(node.end_pos[0], node.end_pos[1])

        if start <= self.cursor_position < end:
            self.found_node = node
            return True

        return False


def get_path_to_pos(tree, pos):
    v = Visitor(cursor_position=pos)
    tree.accept(visitor=v)

    if not v.found_node:
        return []

    path: List[YamlNode] = []
    node = v.found_node
    while node:
        path.insert(0, node)
        node = node.parent
    return path


def get_parent_word(document: Document, position: types.Position):
    lines = document.lines
    if position.line >= len(lines) or position.line == 0:
        return None

    row, col = position_from_utf16(lines, position)    
    
    cur_word = document.word_at_position(position=types.Position(line=row, character=col))
    line = lines[row]
    index = line.find(cur_word)
    if index >= 2:
        col = index - 2
    
    row -= 1
    word = None
    while row >= 0:
        word = document.word_at_position(position=types.Position(line=row, character=col))
        row -= 1
        if word:
            break
    
    return word
    

def preceding_words(document: Document, position: types.Position) -> Optional[Tuple[str, str]]:
    """
    Get the word under the cursor returning the start and end positions.
    """
    lines = document.lines
    if position.line >= len(lines):
        return None

    row, col = position_from_utf16(lines, position)
    line = lines[row]
    try:
        word = line[:col].strip().split()[-2:]
        return word
    except (ValueError):
        return None

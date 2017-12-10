from game_config import *

class Piece:
    def __init__(self, color, kind, code):
        self.color = color
        self.kind = kind
        self.code = code

class Game:
    def __init__(self):
        self.piece = {}

    def __getitem__(self, index):
        return self.piece[index]

    def __setitem__(self, index, value):
        self.piece[index] = value

    def add_piece(self, char, pos):
        if char is None:
            color = None
        elif char.isupper():
            color = RED
        else:
            color = BLACK
        kind = KIND_TABLE[char]
        self.piece[pos] = Piece(color, kind, char)

    def fen_parse(self, fen_str):
        x = 1
        y = 1
        for i in range(0, len(fen_str)):
            char = fen_str[i]
            if char == '/':
                x = 1
                y += 1
            elif char.isdigit():
                for j in range(0,int(char)):
                    self.add_piece(None, (x, y))
                    x += 1
            else:
                self.add_piece(char, (x, y))
                x += 1

    def fen_generate(self):
        fen_str = ""
        t = 0
        for x in range(1, 10):
            for y in range(1, 11):
                if x == 1:
                    fen_str = fen_str + "/"
                if self.piece[(x, y)].code is not None:
                    if t >= 1:
                        fen_str = fen_str + str(t)
                        t = 0
                    fen_str = fen_str + self.piece[(x, y)].code
                else:
                    t = t + 1
        return fen_str

    def move_piece(self, A, B): # move piece from position A to position B
        self.add_piece(self.piece[A].code, B) # move piece from A to B
        self.add_piece(None, A) # delete piece at A

    def check_legal_move(self, A, B):
        def king_legal():
            legal = False
            if abs(B[0]-A[0]+B[1]-A[1]) == 1 and self.piece[B].color != self.piece[A].color:
                if self.piece[A].color == RED:
                    if  B[0] in range(4, 7) and B[1] in range(8, 11):
                        legal = True
                elif B[0] in range(4, 7) and B[1] in range(1, 4):
                    legal = True
            return legal

        def advisor_legal():
            legal = False
            if abs(B[0]-A[0]) == 1 and abs(B[1]-A[1]) == 1 and self.piece[B].color != self.piece[A].color:
                if self.piece[A].color == RED:
                    if  B[0] in range(4, 7) and B[1] in range(8, 11):
                        legal = True
                elif B[0] in range(4, 7) and B[1] in range(1, 4):
                    legal = True
            return legal

        def bishop_legal():
            legal = False
            if abs(B[0] - A[0]) == 2 and abs(B[1] - A[1]) == 2 and \
               self.piece[(B[0] + A[0])/2, (B[1] + A[1])/2].kind is None and \
               self.piece[B].color != self.piece[A].color:
                if self.piece[A].color == RED and B[1] >= 6:
                    legal = True
                elif self.piece[A].color == BLACK and B[1] <= 5:
                    legal = True
            return legal

        def knight_legal():
            legal = False
            if abs(B[0] - A[0]) == 2 and abs(B[1] - A[1]) == 1:
                if self.piece[((B[0] + A[0])/2, A[1])].kind is None and \
                   self.piece[B].color != self.piece[A].color:
                    legal = True
            elif abs(B[0] - A[0]) == 1 and abs(B[1] - A[1]) == 2:
                if self.piece[(A[0], (B[1] + A[1])/2)].kind is None and \
                   self.piece[B].color != self.piece[A].color:
                    legal = True
            return legal

        def rook_legal():
            legal = False
            if B[0] == A[0] and B[1] != A[1] and self.piece[B].color != self.piece[A].color:
                legal = True
                for i in range(1, abs(B[1]-A[1])):  # check if there is any obstacle between 2 points
                    if self.piece[(B[0], min(A[1], B[1]) + i)].kind is not None:
                        legal = False
                        break
            elif B[0] != A[0] and B[1] == A[1] and self.piece[B].color != self.piece[A].color:
                legal = True
                for i in range(1, abs(B[0]-A[0])):  # check if there is any obstacle between 2 points
                    if self.piece[(min(A[0], B[0]) + i, B[1])].kind is not None:
                        legal = False
                        break
            return legal

        def cannon_legal():
            legal = False
            count = 0
            if B[0] == A[0] and B[1] != A[1]:
                for i in range(1, abs(B[1]-A[1])):  # check if there is any obstacle between 2 points
                    if self.piece[(B[0], min(A[1], B[1]) + i)].kind is not None:
                        count+=1
            elif B[0] != A[0] and B[1] == A[1]:
                for i in range(1, abs(B[0]-A[0])):  # check if there is any obstacle between 2 points
                    if self.piece[(min(A[0], B[0]) + i, B[1])].kind is not None:
                        count+=1
            else:
                count = -1
            if count == 0 and self.piece[B].kind is None:
                legal = True
            if count == 1 and self.piece[B].kind is not None and self.piece[B].color != self.piece[A].color:
                legal = True
            return legal

        def pawn_legal():
            legal = False
            if self.piece[A].color == RED and B[1] <= A[1] and self.piece[B].color != self.piece[A].color:
                if A[1] >= 6: # red pawn not over river
                    if A[0]==B[0] and abs(A[1]-B[1])==1:
                        legal = True
                else:
                    if abs(A[1]-B[1]) + abs(A[0]-B[0]) == 1:
                        legal = True
            elif self.piece[A].color == BLACK and B[1] >= A[1] and self.piece[B].color != self.piece[A].color:
                if A[1] <= 5: # black pawn not over river
                    if A[0]==B[0] and abs(A[1]-B[1]) == 1:
                        legal = True
                else:
                    if abs(A[1]-B[1]) + abs(A[0]-B[0]) == 1 :
                        legal = True

            return legal

        check = {KING: king_legal,
                 ADVISOR: advisor_legal,
                 BISHOP: bishop_legal,
                 KNIGHT: knight_legal,
                 ROOK: rook_legal,
                 CANNON: cannon_legal,
                 PAWN: pawn_legal}
        return check[self.piece[A].kind]()

    def get_movename(self, A, B):  # must check legal before get movename
        def movetype_1():  # straight moves for rook, cannon, king, pawn
            if self.piece[A].color == RED:
                if A[1] == B[1]:
                    movename = VN_PIECENAME[self.piece[A].kind]+str(10-A[0])+"-"+str(10-B[0])
                elif A[1] > B[1]:
                    movename = VN_PIECENAME[self.piece[A].kind] + str(10 - A[0]) + "." + str(A[1] - B[1])
                else:
                    movename = VN_PIECENAME[self.piece[A].kind] + str(10 - A[0]) + "/" + str(B[1] - A[1])
            else:
                if A[1] == B[1]:
                    movename = VN_PIECENAME[self.piece[A].kind].lower() + str(A[0]) + "-" + str(B[0])
                elif A[1] > B[1]:
                    movename = VN_PIECENAME[self.piece[A].kind].lower() + str(A[0]) + "/" + str(A[1] - B[1])
                else:
                    movename = VN_PIECENAME[self.piece[A].kind].lower() + str(A[0]) + "." + str(B[1] - A[1])
            return movename

        def movetype_2():  # diagonal moves for knight, bishop, advisor
            if self.piece[A].color == RED:
                if A[1] > B[1]:
                    movename = VN_PIECENAME[self.piece[A].kind] + str(10 - A[0]) + "." + str(10 - B[0])
                else:
                    movename = VN_PIECENAME[self.piece[A].kind] + str(10 - A[0]) + "/" + str(10 - B[0])
            else:
                if A[1] > B[1]:
                    movename = VN_PIECENAME[self.piece[A].kind].lower() + str(A[0]) + "/" + str(B[0])
                else:
                    movename = VN_PIECENAME[self.piece[A].kind].lower() + str(A[0]) + "." + str(B[0])
            return movename

        movetype = {KING: movetype_1,
                    ADVISOR: movetype_2,
                    BISHOP: movetype_2,
                    KNIGHT: movetype_2,
                    ROOK: movetype_1,
                    CANNON: movetype_1,
                    PAWN: movetype_1}
        return movetype[self.piece[A].kind]()

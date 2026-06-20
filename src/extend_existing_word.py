from board import board


def extend_existing_word(actual: list) -> list:
    possibilities = []
    for i in range(len(board)):
        j = 0
        while j < len(board[i]):

            if board[i][j] != 0 and j != len(board[i]) - 1 and board[i][j + 1] != 0:
                word = board[i][j]
                incr = 1
                while True:
                    if board[i][j + incr] != 0:
                        if j + incr == len(board[i]) - 1:
                            word += board[i][j + incr]
                            j = len(board[i]) - 1
                            break
                        else:
                            word += board[i][j + incr]
                            incr += 1

                    else:
                        j += incr
                        break

                possibilities.append([word, ((i, j), (i, j + incr))])

            else:
                j += 1

    for i in range(len(board)):
        j = 0
        while j < len(board[i]):

            if board[j][i] != 0 and j != len(board) - 1 and board[j + 1][i] != 0:
                word = board[j][i]
                incr = 1
                while True:
                    if board[j + incr][i] != 0:
                        if j + incr == len(board) - 1:
                            word += board[j + incr][i]
                            j = len(board) - 1
                            break
                        else:
                            word += board[j + incr][i]
                            incr += 1

                    else:
                        j += incr
                        break

                possibilities.append([word, ((j, i), (j + incr, i))])

            else:
                j += 1

    print(possibilities)


extend_existing_word(board)

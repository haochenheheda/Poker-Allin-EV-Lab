import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QHBoxLayout, QLineEdit, QVBoxLayout, QLabel, QButtonGroup, QRadioButton
from functools import partial
from PyQt5.QtGui import QColor, QPalette

card_map = {12:'2', 11:'3', 10:'4', 9:'5', 8:'6', 7:'7', 6:'8', 5:'9', 4:'T', 3:'J', 2:'Q', 1:'K', 0:'A'}
reversed_card_map = {'2':12, '3':11, '4':10, '5':9, '6':8, '7':7, '8':6, '9':5, 'T':4, 'J':3, 'Q':2, 'K':1, 'A':0}

#just for sorting
nums = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm']
nums_dic = {'a':12, 'b':11, 'c':10, 'd':9, 'e':8, 'f':7, 'g':6, 'h':5, 'i':4, 'j':3, 'k':2, 'l':1, 'm':0}
colors = ['1', '2', '3', '4']

cards = []
for num in nums:
    for color in colors:
        cards.append(num + color)

ghands = []

for card1 in cards:
    for card2 in cards:
        if card1 < card2:
            ghands.append([card1, card2])


# Create a subclass of QMainWindow to define your main window
class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("坤坤Lab")
        self.setGeometry(100, 100, 1280, 720)  # (x, y, width, height)
        
        self.winrate = np.load('winrate.npy')
        self.valid_range = (self.winrate >= 0).astype(np.float32)
        self.winrate[self.winrate < 0] = 0.
        

        # Create widgets
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        left_grid_layout = QGridLayout()
        right_grid_layout = QGridLayout()
        v_layout = QVBoxLayout()

        self.left_buttons = []
        self.left_buttons_states = []
        self.right_buttons = []

        num_rows, num_cols = 13, 13
        for row in range(num_rows):
            tmp_right_buttons = []
            tmp_left_buttons = []
            tmp_left_buttons_states = []
            for col in range(num_cols):
                if row > col:
                    hands = card_map[col] + card_map[row] + 'o'
                elif row < col:
                    hands = card_map[row] + card_map[col] + 's'
                else:
                    hands = card_map[col] + card_map[row]
                
                lbutton = QPushButton(hands)
                rbutton = QPushButton(hands)
                style = f"font-size: {8}px;"
                lbutton.setStyleSheet(style)
                rbutton.setStyleSheet(style)
                lbutton.setFixedSize(50,50)
                rbutton.setFixedSize(50,50)

                lbutton.clicked.connect(partial(self.onClick, hands))
                left_grid_layout.addWidget(lbutton, row, col)
                right_grid_layout.addWidget(rbutton, row, col)
                tmp_left_buttons.append(lbutton)
                tmp_right_buttons.append(rbutton)
                tmp_left_buttons_states.append(False)
            self.left_buttons.append(tmp_left_buttons)
            self.right_buttons.append(tmp_right_buttons)
            self.left_buttons_states.append(tmp_left_buttons_states)

        layout.addLayout(left_grid_layout)
        layout.addLayout(right_grid_layout)
        layout.addLayout(v_layout)

        button_margin = 3

        left_grid_layout.setSpacing(button_margin)
        right_grid_layout.setSpacing(button_margin)
        left_grid_layout.setVerticalSpacing(button_margin)
        right_grid_layout.setVerticalSpacing(button_margin)


        self.button = QPushButton("Compute", self)
        v_layout.addWidget(self.button)
        self.button.clicked.connect(self.compute)

        self.button_group = QButtonGroup()
        self.option1_radio = QRadioButton("Call Allin")
        self.option2_radio = QRadioButton("Allin")

        self.option1_radio.setChecked(True)  # Set the default option

        self.button_group.addButton(self.option1_radio)
        self.button_group.addButton(self.option2_radio)

        v_layout.addWidget(self.option1_radio)
        v_layout.addWidget(self.option2_radio)
 

        potBBlabel = QLabel("Pot BB:")
        v_layout.addWidget(potBBlabel)

        self.potBBbox = QLineEdit()
        v_layout.addWidget(self.potBBbox)
        self.potBBbox.setText("0")
        self.potBB = 0

        callBBlabel = QLabel("Call/Allin BB:")
        v_layout.addWidget(callBBlabel)

        self.callBBbox = QLineEdit()
        v_layout.addWidget(self.callBBbox)
        self.callBBbox.setText("0")
        self.callBB = 0

        StealRatioLabel = QLabel("Steal Ratio:")
        v_layout.addWidget(StealRatioLabel)

        self.stealRatioBox = QLineEdit()
        v_layout.addWidget(self.stealRatioBox)
        self.stealRatioBox.setText("0")
        self.stealRatio = 0


    def onClick(self, hands):
        print(hands)
        if len(hands) == 2:
           row = reversed_card_map[hands[0]]
           col = reversed_card_map[hands[1]]
        elif hands[-1] == 'o':
           row = reversed_card_map[hands[1]]
           col = reversed_card_map[hands[0]]
        elif hands[-1] == 's':
           row = reversed_card_map[hands[0]]
           col = reversed_card_map[hands[1]]
        if self.left_buttons_states[row][col]:
            self.left_buttons_states[row][col] = False
        else:
            self.left_buttons_states[row][col] = True
        if self.left_buttons_states[row][col] == True:
            self.set_button_background_color(self.left_buttons[row][col], (0, 220, 0))
        if self.left_buttons_states[row][col] == False:
            self.set_button_background_color(self.left_buttons[row][col], (0, 0, 0))

    def set_button_background_color(self, button, color):
        button.setStyleSheet("font-size: 8px; color: rgb{};".format(str(color)))
        #palette = QPalette()
        #palette.setColor(QPalette.Button, color)
        #button.setAutoFillBackground(True)
        #button.setPalette(palette)
        
    def compute(self):
        selected_option_id = self.button_group.checkedId()
        if selected_option_id == -2:
            self.potBB = float(self.potBBbox.text())
            self.callBB = float(self.callBBbox.text())
           
            self.right_ev_list = [[0 for _ in range(13)] for _ in range(13)]
                
            self.range = np.zeros(1326)
            for idx, hand in enumerate(ghands):
                hand = hand[0] + hand[1]
                assert hand[2] >= hand[0]
                if hand[2] == hand[0]:
                    row = nums_dic[hand[0]]
                    col = nums_dic[hand[0]]
                elif hand[2] > hand[0]:
                    if hand[3] == hand[1]:
                        col = nums_dic[hand[0]]
                        row = nums_dic[hand[2]]
                    elif hand[3] != hand[1]:
                        col = nums_dic[hand[2]]
                        row = nums_dic[hand[0]]
                if self.left_buttons_states[row][col] == True:
                    self.range[idx] = 1.
            hands_winrate = np.dot(self.winrate, self.range)
            norm = np.dot(self.valid_range, self.range)
            all_winrate_array = hands_winrate / norm
            
            for idx, hand in enumerate(ghands):
                hand_winrate = all_winrate_array[idx]
                hand = hand[0] + hand[1]
                assert hand[2] >= hand[0]
                if hand[2] == hand[0]:
                    row = nums_dic[hand[0]]
                    col = nums_dic[hand[0]]
                elif hand[2] > hand[0]:
                    if hand[3] == hand[1]:
                        col = nums_dic[hand[0]]
                        row = nums_dic[hand[2]]
                    elif hand[3] != hand[1]:
                        col = nums_dic[hand[2]]
                        row = nums_dic[hand[0]]
                self.right_ev_list[row][col] += hand_winrate * (self.potBB + self.callBB) - self.callBB


            #norm
            for row in range(13):
                for col in range(13):
                    if row == col:
                        self.right_ev_list[row][col] /= 6
                    elif row < col:
                        self.right_ev_list[row][col] /= 4
                    elif row > col:
                        self.right_ev_list[row][col] /= 12

                    if row > col:
                        hands = card_map[col] + card_map[row] + 'o'
                    elif row < col:
                        hands = card_map[row] + card_map[col] + 's'
                    else:
                        hands = card_map[col] + card_map[row]
                    if self.right_ev_list[row][col] > 0:
                        self.set_button_background_color(self.right_buttons[row][col], (0, 220, 0))
                    else:
                        self.set_button_background_color(self.right_buttons[row][col], (0, 0, 0))


                    self.right_buttons[row][col].setText(hands + '\n' + '{:.2f}'.format(self.right_ev_list[row][col]))


        elif selected_option_id == -3:
            self.potBB = float(self.potBBbox.text())
            self.allinBB = float(self.callBBbox.text())
            self.stealRatio = float(self.stealRatioBox.text())
           
            self.right_ev_list = [[0 for _ in range(13)] for _ in range(13)]
                
            self.range = np.zeros(1326)
            for idx, hand in enumerate(ghands):
                hand = hand[0] + hand[1]
                assert hand[2] >= hand[0]
                if hand[2] == hand[0]:
                    row = nums_dic[hand[0]]
                    col = nums_dic[hand[0]]
                elif hand[2] > hand[0]:
                    if hand[3] == hand[1]:
                        col = nums_dic[hand[0]]
                        row = nums_dic[hand[2]]
                    elif hand[3] != hand[1]:
                        col = nums_dic[hand[2]]
                        row = nums_dic[hand[0]]
                if self.left_buttons_states[row][col] == True:
                    self.range[idx] = 1.
            hands_winrate = np.dot(self.winrate, self.range)
            norm = np.dot(self.valid_range, self.range)
            all_winrate_array = hands_winrate / norm
            
            for idx, hand in enumerate(ghands):
                hand_winrate = all_winrate_array[idx]
                hand = hand[0] + hand[1]
                assert hand[2] >= hand[0]
                if hand[2] == hand[0]:
                    row = nums_dic[hand[0]]
                    col = nums_dic[hand[0]]
                elif hand[2] > hand[0]:
                    if hand[3] == hand[1]:
                        col = nums_dic[hand[0]]
                        row = nums_dic[hand[2]]
                    elif hand[3] != hand[1]:
                        col = nums_dic[hand[2]]
                        row = nums_dic[hand[0]]
                self.right_ev_list[row][col] += self.stealRatio * self.potBB + (1 - self.stealRatio) * (hand_winrate * (self.potBB + self.allinBB * 2) - self.allinBB)


            #norm
            for row in range(13):
                for col in range(13):
                    if row == col:
                        self.right_ev_list[row][col] /= 6
                    elif row < col:
                        self.right_ev_list[row][col] /= 4
                    elif row > col:
                        self.right_ev_list[row][col] /= 12

                    if row > col:
                        hands = card_map[col] + card_map[row] + 'o'
                    elif row < col:
                        hands = card_map[row] + card_map[col] + 's'
                    else:
                        hands = card_map[col] + card_map[row]
                    if self.right_ev_list[row][col] > 0:
                        self.set_button_background_color(self.right_buttons[row][col], (0, 220, 0))
                    else:
                        self.set_button_background_color(self.right_buttons[row][col], (0, 0, 0))


                    self.right_buttons[row][col].setText(hands + '\n' + '{:.2f}'.format(self.right_ev_list[row][col]))


 
                




            
        
        
        

def main():
    # Create the PyQt5 application
    app = QApplication(sys.argv)

    # Create the main window
    window = MyMainWindow()

    # Show the main window
    window.show()

    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


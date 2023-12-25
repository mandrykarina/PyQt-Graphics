import sys
import pyqtgraph as pg

from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QTableWidgetItem, QFileDialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QTableWidget
from PyQt5.QtGui import QPixmap, QIcon

import sqlite3
import datetime


# основной класс
class MyWidget(QMainWindow, QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('desin5widggwidee4.ui', self)  # Загружаем дизайн
        self.historybutton.clicked.connect(self.open_second_form)

        # добавление картинки на фон
        label = QLabel(self)
        pixmap = QPixmap('paradise.jpg')
        label.setPixmap(pixmap)
        self.setWindowTitle('FuncBuilder')
        self.setFixedWidth(780)
        self.setFixedHeight(720)

        self.graphWidget = pg.PlotWidget()
        # опредление и добавление графика в виджет
        self.pen = pg.mkPen(color=(255, 0, 0))
        self.companovka_for_mpl = QVBoxLayout(self.widget)
        self.companovka_for_mpl.addWidget(self.graphWidget)

        self.buildgrafbutton.clicked.connect(self.build_graf)

        self.savebutton.clicked.connect(self.save_graph)

    # сохранение фото графика
    def save_graph(self):
        '''
        Сохранение изображение графика функции в директорию пользователя.
        '''
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить график", "",
                                                   "Изображения (*.png);;All Files (*)",
                                                   options=options)

        if file_path:
            # Копируем изображение из буфера обмена и сохраняем его в файл
            img = self.graphWidget.grab()
            img.save(file_path)

            msg = QMessageBox()
            msg.setText("Сохранено")
            msg.setWindowTitle("Готово")
            msg.setWindowIcon(QIcon("t.jpg"))
            msg.setIcon(QMessageBox.Information)
            msg.setStyleSheet("QLabel{ color: purple}")
            msg.exec_()

    def build_graf(self):
        '''
        Построение графика функции. Параметры функции беруться из поля
        '''
        # вызов окна ошибки если текст не был введен
        if not self.function.text():
            msg = ErrorWidgets()
            msg.NotData()
            msg.exec_()
            return

        text_func = self.function.text()

        # флаг, учитывающий, есть ли ошибки. Когда он True, значит ошибок не возникло, иначе False
        isGood = True
        for j in range(len(text_func) - 1):
            if (text_func[j].isalpha() and text_func[j + 1].isdigit()) or (
                    text_func[j + 1].isalpha() and text_func[j].isdigit()):
                isGood = False
                msg = ErrorWidgets()
                msg.NoSign()
                msg.exec_()
                return

        # создание массивов точек
        xdots = []
        ydots = []
        for x in range(1, 8):
            for i in text_func:
                if i.isalpha() and i != 'x':
                    text_func = text_func.replace(i, 'x')
                if i == ':':
                    text_func = text_func.replace(i, '/')
            try:
                y = eval(text_func)
                ydots.append(y)
                xdots.append(x)

            except ZeroDivisionError:
                isGood = False
                msg = ErrorWidgets()
                msg.DivisionByZero()
                msg.exec_()
                break

            except SyntaxError:
                isGood = False
                msg = ErrorWidgets()
                msg.InputError()
                msg.exec_()
                break

            except NameError:
                isGood = False
                msg = ErrorWidgets()
                msg.InputError()
                msg.exec_()
                break
        if isGood:
            # добавление в бд
            insertQuery = """INSERT INTO functionsss
                                                                    VALUES (?, ?);"""
            cursor.execute(insertQuery, (datetime.datetime.now(), f'{text_func}'))
            connect.commit()

        # очищение графика и отрисовка нового
        self.graphWidget.clear()
        self.graphWidget.plot(xdots, ydots, pen=self.pen)

    def open_second_form(self):
        '''
        Открывает вторую форму для компонента "истории".
        '''
        self.second_form = SecondForm(self, "Данные для второй формы")
        self.second_form.show()


# выведение данных об истории в табличном виде
class SecondForm(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    def initUI(self, args):
        '''
        Инициализация пользовательского интерфейса.
        '''
        self.setGeometry(100, 200, 800, 600)
        self.setWindowTitle('История')
        self.lbl = QLabel(args[-1], self)
        self.lbl.adjustSize()

        label = QLabel(self)
        pixmap = QPixmap('paradise.jpg')
        label.setPixmap(pixmap)
        self.setFixedWidth(400)
        self.setFixedHeight(300)
        self.setWindowTitle('History')

        # создание таблицы и добавление в нее информации из бд
        self.tableWidget = QTableWidget(self)
        self.tableWidget.move(70, 70)
        cursor.execute("""SELECT * FROM functionsss""")
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(['time', 'func'])
        for row, form in enumerate(cursor):
            self.tableWidget.insertRow(row)
            for column, item in enumerate(form):
                print(str(item))
                self.tableWidget.setItem(row, column, QTableWidgetItem(str(item)))


# класс содержащий в себе виджет, объявляющий об ошибках
class ErrorWidgets(QMessageBox):
    def __init__(self):
        super().__init__()

    def NotData(self):
        '''
        Сообщение об ошибке, когда нет данных в пользовательской строке для построения графика.
        '''
        self.setText("Вы ничего не ввели, записывать нечего.")
        self.setWindowTitle("Внимание")
        self.setWindowIcon(QIcon("s.jpg"))
        self.setIcon(QMessageBox.Information)
        self.setStyleSheet("QLabel{ color: purple}")

        return self

    def NoSign(self):
        '''
        Сообщение об ошибке, когда забыли добавить знак умножения перед аргументом.
        К премеру ввели: 3x, а следовало ввести 3 * x.
        '''
        self.setText("Где-то Вы забыли знак умножить, пожалуйста введите функцию заново")
        self.setWindowTitle("Внимание")
        self.setWindowIcon(QIcon("s.jpg"))
        self.setIcon(QMessageBox.Information)
        self.setStyleSheet("QLabel{ color: purple}")
        return self

    def DivisionByZero(self):
        '''
        Сообщение об ошибке, когда попытались построить график функции с математической ошибкой- Деление на ноль
        '''
        self.setText("Делить на ноль нельзя!\nИзмените функцию и попробуйте снова.")
        self.setWindowTitle("Внимание")
        self.setWindowIcon(QIcon("s.jpg"))
        self.setIcon(QMessageBox.Information)
        self.setStyleSheet("QLabel{ color: purple}")
        return self

    def InputError(self):
        '''
        Сообщение об ошибке, когда попытались ввести некорректные данные.
        '''
        self.setText("Данные введены некорректно!\nИзмените функцию и попробуйте снова.")
        self.setWindowTitle("Внимание")
        self.setWindowIcon(QIcon("s.jpg"))
        self.setIcon(QMessageBox.Information)
        self.setStyleSheet("QLabel{ color: purple}")
        return self


def create_database():
    '''
    Создание базы данных SQLite. Если такая уже есть, то просто подключиться к ней.
    '''
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS functionsss(
            time TIMESTAMP, 
            func TEXT
        )'''
    )
    connect.commit()


# переменная для работы с внешними подключениями базы данных
connect = sqlite3.connect('database.sqlite')
# переменная для работы с данными внутри базы данных
cursor = connect.cursor()

if __name__ == '__main__':
    # создаем подключение к базе данных
    create_database()
    # создаем инициализацию приложения
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())

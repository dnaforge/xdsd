# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow_nodraw.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1420, 1049)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.left_box = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.left_box.sizePolicy().hasHeightForWidth())
        self.left_box.setSizePolicy(sizePolicy)
        self.left_box.setMinimumSize(QtCore.QSize(400, 0))
        self.left_box.setMaximumSize(QtCore.QSize(600, 16777215))
        self.left_box.setObjectName("left_box")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.left_box)
        self.verticalLayout_5.setObjectName("verticalLayout_5")

        self.simulation_box = QtWidgets.QTabWidget(self.left_box)
        self.simulation_box.setObjectName("simulation_box")
        self.simulation_tab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.simulation_box.sizePolicy().hasHeightForWidth())
        self.simulation_box.setSizePolicy(sizePolicy)
        self.simulation_box.setMaximumHeight(150)
        self.simulation_tab.setObjectName("simulation_tab")
        self.verticalLayoutSim = QtWidgets.QVBoxLayout(self.simulation_tab)
        self.simulationUpWidget = QtWidgets.QWidget(self.simulation_tab)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.simulationUpWidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.generate_button = QtWidgets.QPushButton(self.simulationUpWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.generate_button.sizePolicy().hasHeightForWidth())
        self.generate_button.setSizePolicy(sizePolicy)
        self.generate_button.setMinimumSize(QtCore.QSize(200, 30))
        self.generate_button.setMaximumSize(QtCore.QSize(200, 30))
        self.generate_button.setObjectName("generate_button")
        self.horizontalLayout_3.addWidget(self.generate_button)
        self.generate_stop_button = QtWidgets.QPushButton(self.simulationUpWidget)
        self.generate_stop_button.setObjectName("generate_stop_button")
        self.horizontalLayout_3.addWidget(self.generate_stop_button)
        self.verticalLayoutSim.addWidget(self.simulationUpWidget)

        self.simulationDownWidget = QtWidgets.QWidget(self.simulation_tab)
        self.simulationDownWidget.setObjectName("widget_3")
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout(self.simulationDownWidget)
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.simulate_button = QtWidgets.QPushButton(self.simulationDownWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.simulate_button.sizePolicy().hasHeightForWidth())
        self.simulate_button.setSizePolicy(sizePolicy)
        self.simulate_button.setMinimumSize(QtCore.QSize(200, 30))
        self.simulate_button.setMaximumSize(QtCore.QSize(200, 30))
        self.simulate_button.setObjectName("simulate_button")
        self.horizontalLayout_16.addWidget(self.simulate_button)
        self.simulate_combo = QtWidgets.QComboBox(self.simulationDownWidget)
        self.simulate_combo.setObjectName("simulate_combo")
        self.simulate_combo.addItem("")
        self.simulate_combo.addItem("")
        self.horizontalLayout_16.addWidget(self.simulate_combo)
        self.verticalLayoutSim.addWidget(self.simulationDownWidget)
        self.simulation_box.addTab(self.simulation_tab, "")
        self.verticalLayout_5.addWidget(self.simulation_box)

        # LEFT DSD INPUT
        self.input_box = QtWidgets.QTabWidget(self.left_box)
        self.input_box.setObjectName("input_box")
        self.code_tab = QtWidgets.QWidget()
        self.input_box.addTab(self.code_tab, "DSD model")
        self.code_tab.setObjectName("code_tab")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.code_tab)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.file_buttons_widget = QtWidgets.QWidget(self.code_tab)
        self.file_buttons_widget.setObjectName("file_buttons_widget")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.file_buttons_widget)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.open_button = QtWidgets.QPushButton(self.file_buttons_widget)
        self.open_button.setObjectName("open_button")
        self.horizontalLayout_9.addWidget(self.open_button)
        spacerItem = QtWidgets.QSpacerItem(64, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem)
        self.save_button = QtWidgets.QPushButton(self.file_buttons_widget)
        self.save_button.setObjectName("save_button")
        self.horizontalLayout_9.addWidget(self.save_button)
        self.show_button = QtWidgets.QPushButton(self.file_buttons_widget)
        self.show_button.setObjectName("show_button")
        self.horizontalLayout_9.addWidget(self.show_button)
        self.verticalLayout_8.addWidget(self.file_buttons_widget)
        self.code_text = QtWidgets.QTextEdit(self.code_tab)
        self.code_text.setObjectName("code_text")
        self.verticalLayout_8.addWidget(self.code_text)
        # self.verticalLayout_8.addWidget(self.code_tab)

        # LEFT RENDERING OPTION
        self.render_option_tab = QtWidgets.QWidget()
        self.input_box.addTab(self.render_option_tab, "Rendering options")
        self.verticalLayout_88 = QtWidgets.QVBoxLayout(self.render_option_tab)

        self.file_buttons_widget2 = QtWidgets.QWidget(self.render_option_tab)
        self.file_buttons_widget.setObjectName("file_buttons_widget2")
        self.horizontalLayout_99 = QtWidgets.QHBoxLayout(self.file_buttons_widget2)
        self.horizontalLayout_99.setObjectName("horizontalLayout_99")
        spacerItem = QtWidgets.QSpacerItem(64, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_99.addItem(spacerItem)
        self.show_button2 = QtWidgets.QPushButton(self.file_buttons_widget2)
        self.show_button2.setObjectName("show_button2")
        self.horizontalLayout_99.addWidget(self.show_button2)
        self.verticalLayout_88.addWidget(self.file_buttons_widget2)

        self.groupBox_3 = QtWidgets.QGroupBox(self.render_option_tab)
        self.groupBox_3.setObjectName("groupBox_3")
        self.groupBox_3.setMaximumHeight(100)
        self.horizontalLayout_55 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_55.setObjectName("horizontalLayout_55")
        self.slider_value_label2 = QtWidgets.QLabel(self.groupBox_3)
        self.slider_value_label2.setObjectName("slider_value_label2")
        self.slider_value_label2.setFixedWidth(50)
        self.horizontalLayout_55.addWidget(self.slider_value_label2)
        self.threshold_slider2 = QtWidgets.QSlider(self.groupBox_3)
        self.threshold_slider2.setMinimumSize(QtCore.QSize(100, 0))
        self.threshold_slider2.setMaximumSize(QtCore.QSize(275, 16777215))
        self.threshold_slider2.setMinimum(0)
        self.threshold_slider2.setMaximum(500)
        self.threshold_slider2.setProperty("value", 100)
        self.threshold_slider2.setOrientation(QtCore.Qt.Horizontal)
        self.threshold_slider2.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.threshold_slider2.setTickInterval(10)
        self.threshold_slider2.setObjectName("threshold_slider2")
        self.horizontalLayout_55.addWidget(self.threshold_slider2)
        self.verticalLayout_88.addWidget(self.groupBox_3)

        self.groupBox_33 = QtWidgets.QGroupBox("Layout", self.render_option_tab)
        self.verticalLayout_33 = QtWidgets.QVBoxLayout(self.groupBox_33)
        self.straight_radio = QtWidgets.QRadioButton("Straight-line layout", self.groupBox_33)
        self.straight_radio.setChecked(True)
        self.verticalLayout_33.addWidget(self.straight_radio)
        self.ortho_radio = QtWidgets.QRadioButton("Orthogonal layout", self.groupBox_33)
        self.verticalLayout_33.addWidget(self.ortho_radio)
        self.verticalLayout_88.addWidget(self.groupBox_33)

        spacerItem3 = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_88.addItem(spacerItem3)

        self.optimization_tab = QtWidgets.QWidget()
        self.optimization_tab.setObjectName("optimization_tab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.optimization_tab)
        self.verticalLayout.setObjectName("verticalLayout")

        self.optimization_widget = QtWidgets.QWidget(self.optimization_tab)
        self.optimization_widget.setObjectName("optimization_widget")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.optimization_widget)
        self.verticalLayout_7.setObjectName("verticalLayout_7")

        self.groupBox_2 = QtWidgets.QGroupBox(self.optimization_widget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.slider_value_label = QtWidgets.QLabel(self.groupBox_2)
        self.slider_value_label.setObjectName("slider_value_label")
        self.slider_value_label.setFixedWidth(75)
        self.horizontalLayout_5.addWidget(self.slider_value_label)
        self.threshold_slider = QtWidgets.QSlider(self.groupBox_2)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.threshold_slider.sizePolicy().hasHeightForWidth())
        # self.threshold_slider.setSizePolicy(sizePolicy)
        self.threshold_slider.setMinimumSize(QtCore.QSize(100, 0))
        self.threshold_slider.setMaximumSize(QtCore.QSize(275, 16777215))
        self.threshold_slider.setMinimum(1)
        self.threshold_slider.setMaximum(8)
        self.threshold_slider.setProperty("value", 7)
        self.threshold_slider.setOrientation(QtCore.Qt.Horizontal)
        self.threshold_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.threshold_slider.setTickInterval(1)
        self.threshold_slider.setObjectName("threshold_slider")
        self.horizontalLayout_5.addWidget(self.threshold_slider)
        self.verticalLayout_7.addWidget(self.groupBox_2)

        # spacerItem3 = QtWidgets.QSpacerItem(20, 50, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # self.verticalLayout_7.addItem(spacerItem3)

        self.verticalLayout.addWidget(self.optimization_widget)
        self.simulation_box.addTab(self.optimization_tab, "")
        self.verticalLayout_5.addWidget(self.input_box)
        self.horizontalLayout.addWidget(self.left_box)
        spacerItem4 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.right_box = QtWidgets.QWidget(self.centralwidget)
        self.right_box.setObjectName("right_box")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.right_box)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.output_toolbar = QtWidgets.QTabWidget(self.right_box)
        self.output_toolbar.setEnabled(True)
        self.output_toolbar.setIconSize(QtCore.QSize(16, 16))
        self.output_toolbar.setElideMode(QtCore.Qt.ElideNone)
        self.output_toolbar.setDocumentMode(False)
        self.output_toolbar.setTabsClosable(False)
        self.output_toolbar.setMovable(False)
        self.output_toolbar.setProperty("tabBarAutoHide", False)
        self.output_toolbar.setObjectName("output_toolbar")
        self.canvas_tab = QtWidgets.QWidget()
        self.canvas_tab.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas_tab.sizePolicy().hasHeightForWidth())
        self.canvas_tab.setSizePolicy(sizePolicy)
        self.canvas_tab.setObjectName("canvas_tab")
        self.canvas_layout = QtWidgets.QVBoxLayout(self.canvas_tab)
        self.canvas_layout.setContentsMargins(8, 8, 8, 8)
        self.canvas_layout.setObjectName("canvas_layout")
        self.canvas_top_widget = QtWidgets.QWidget(self.canvas_tab)
        self.canvas_top_widget.setObjectName("canvas_top_widget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.canvas_top_widget)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem5 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem5)
        self.canvas_save = QtWidgets.QPushButton(self.canvas_top_widget)
        self.canvas_save.setObjectName("canvas_save")
        self.horizontalLayout_4.addWidget(self.canvas_save)
        self.canvas_layout.addWidget(self.canvas_top_widget)
        self.canvas_view = QtWidgets.QGraphicsView(self.canvas_tab)
        self.canvas_view.setObjectName("canvas_view")
        self.canvas_layout.addWidget(self.canvas_view)
        self.output_toolbar.addTab(self.canvas_tab, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_15.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.canvas_top_widget_2 = QtWidgets.QWidget(self.tab)
        self.canvas_top_widget_2.setObjectName("canvas_top_widget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.canvas_top_widget_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem6 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem6)
        self.canvas_save_2 = QtWidgets.QPushButton(self.canvas_top_widget_2)
        self.canvas_save_2.setObjectName("canvas_save_2")
        self.horizontalLayout_2.addWidget(self.canvas_save_2)
        self.verticalLayout_15.addWidget(self.canvas_top_widget_2)
        self.canvas_view_2 = QtWidgets.QGraphicsView(self.tab)
        self.canvas_view_2.setObjectName("canvas_view_2")
        self.verticalLayout_15.addWidget(self.canvas_view_2)
        self.output_toolbar.addTab(self.tab, "")
        self.network_tab = QtWidgets.QWidget()
        self.network_tab.setObjectName("network_tab")
        self.network_layout = QtWidgets.QVBoxLayout(self.network_tab)
        self.network_layout.setContentsMargins(8, 8, 8, 8)
        self.network_layout.setObjectName("network_layout")
        self.network_widget = QtWidgets.QWidget(self.network_tab)
        self.network_widget.setObjectName("network_widget")
        self.verticalLayout_16 = QtWidgets.QVBoxLayout(self.network_widget)
        self.verticalLayout_16.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.canvas_top_widget_3 = QtWidgets.QWidget(self.network_widget)
        self.canvas_top_widget_3.setObjectName("canvas_top_widget_3")
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout(self.canvas_top_widget_3)
        self.horizontalLayout_17.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.network_combo = QtWidgets.QComboBox(self.canvas_top_widget_3)
        self.network_combo.setObjectName("network_combo")
        self.network_combo.addItem("")
        self.network_combo.addItem("")
        self.network_combo.addItem("")
        self.network_combo.addItem("")
        self.network_combo.addItem("")
        self.horizontalLayout_17.addWidget(self.network_combo)
        self.species_combo = QtWidgets.QComboBox(self.canvas_top_widget_3)
        self.species_combo.setObjectName("species_combo")
        self.species_combo.addItem("")
        self.horizontalLayout_17.addWidget(self.species_combo)
        spacerItem7 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_17.addItem(spacerItem7)
        self.canvas_save_3 = QtWidgets.QPushButton(self.canvas_top_widget_3)
        self.canvas_save_3.setObjectName("canvas_save_3")
        self.horizontalLayout_17.addWidget(self.canvas_save_3)
        self.verticalLayout_16.addWidget(self.canvas_top_widget_3)
        self.network_layout.addWidget(self.network_widget)
        self.network_view = QtWidgets.QFrame(self.network_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.network_view.sizePolicy().hasHeightForWidth())
        self.network_view.setSizePolicy(sizePolicy)
        self.network_view.setFrameShape(QtWidgets.QFrame.Panel)
        self.network_view.setFrameShadow(QtWidgets.QFrame.Plain)
        self.network_view.setLineWidth(1)
        self.network_view.setObjectName("network_view")
        self.network_layout.addWidget(self.network_view)
        self.output_toolbar.addTab(self.network_tab, "")
        self.graph_tab = QtWidgets.QWidget()
        self.graph_tab.setObjectName("graph_tab")
        self.graph_layout = QtWidgets.QVBoxLayout(self.graph_tab)
        self.graph_layout.setContentsMargins(8, 8, 8, 8)
        self.graph_layout.setObjectName("graph_layout")
        self.graph_widget = QtWidgets.QWidget(self.graph_tab)
        self.graph_widget.setObjectName("graph_widget")
        self.graph_layout.addWidget(self.graph_widget)
        self.output_toolbar.addTab(self.graph_tab, "")
        self.text_output_tab = QtWidgets.QWidget()
        self.text_output_tab.setObjectName("text_output_tab")
        self.text_output_layout = QtWidgets.QVBoxLayout(self.text_output_tab)
        self.text_output_layout.setContentsMargins(8, 8, 8, 8)
        self.text_output_layout.setObjectName("text_output_layout")
        self.widget_2 = QtWidgets.QWidget(self.text_output_tab)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        spacerItem8 = QtWidgets.QSpacerItem(735, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem8)
        self.text_output_save = QtWidgets.QPushButton(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_output_save.sizePolicy().hasHeightForWidth())
        self.text_output_save.setSizePolicy(sizePolicy)
        self.text_output_save.setObjectName("text_output_save")
        self.horizontalLayout_6.addWidget(self.text_output_save)
        self.text_output_layout.addWidget(self.widget_2)
        self.text_output = QtWidgets.QTextEdit(self.text_output_tab)
        self.text_output.setReadOnly(True)
        self.text_output.setObjectName("text_output")
        self.text_output_layout.addWidget(self.text_output)
        self.output_toolbar.addTab(self.text_output_tab, "")
        self.verticalLayout_3.addWidget(self.output_toolbar)
        self.terminal = QtWidgets.QTabWidget(self.right_box)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.terminal.sizePolicy().hasHeightForWidth())
        self.terminal.setSizePolicy(sizePolicy)
        self.terminal.setMinimumSize(QtCore.QSize(0, 200))
        self.terminal.setObjectName("terminal")
        self.terminal_output = QtWidgets.QWidget()
        self.terminal_output.setObjectName("terminal_output")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.terminal_output)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.terminal_output_text = QtWidgets.QTextEdit(self.terminal_output)
        self.terminal_output_text.setReadOnly(True)
        self.terminal_output_text.setObjectName("terminal_output_text")
        self.verticalLayout_10.addWidget(self.terminal_output_text)
        self.terminal.addTab(self.terminal_output, "")
        self.terminal_error = QtWidgets.QWidget()
        self.terminal_error.setObjectName("terminal_error")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.terminal_error)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.terminal_error_text = QtWidgets.QTextEdit(self.terminal_error)
        self.terminal_error_text.setReadOnly(True)
        self.terminal_error_text.setObjectName("terminal_error_text")
        self.verticalLayout_11.addWidget(self.terminal_error_text)
        self.terminal.addTab(self.terminal_error, "")
        self.verticalLayout_5.addWidget(self.terminal)
        self.horizontalLayout.addWidget(self.right_box)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.output_toolbar.setCurrentIndex(0)
        self.terminal.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.generate_button.setText(_translate("MainWindow", "Generate"))
        self.generate_stop_button.setText(_translate("MainWindow", "Stop"))
        self.simulate_button.setText(_translate("MainWindow", "Simulate"))
        self.simulate_combo.setItemText(0, _translate("MainWindow", "Stochastic"))
        self.simulate_combo.setItemText(1, _translate("MainWindow", "Deterministic"))
        self.open_button.setText(_translate("MainWindow", "Open"))
        self.save_button.setText(_translate("MainWindow", "Save"))
        self.show_button.setText(_translate("MainWindow", "Show"))
        self.show_button2.setText(_translate("MainWindow", "Show"))
        self.simulation_box.setTabText(self.simulation_box.indexOf(self.simulation_tab),
                                       _translate("MainWindow", "Simulate"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Generation threshold"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Drawing precision"))
        self.slider_value_label.setText(_translate("MainWindow", "7 iterations"))
        self.slider_value_label2.setText(_translate("MainWindow", "100"))
        self.simulation_box.setTabText(self.simulation_box.indexOf(self.optimization_tab),
                                       _translate("MainWindow", "Simulation options"))
        self.canvas_save.setText(_translate("MainWindow", "Save"))
        self.output_toolbar.setTabText(self.output_toolbar.indexOf(self.canvas_tab),
                                       _translate("MainWindow", "Input view"))
        self.canvas_save_2.setText(_translate("MainWindow", "Save"))
        self.output_toolbar.setTabText(self.output_toolbar.indexOf(self.tab), _translate("MainWindow", "Output view"))
        self.network_combo.setItemText(0, _translate("MainWindow", "Choose network view"))
        self.network_combo.setItemText(1, _translate("MainWindow", "Tree"))
        self.network_combo.setItemText(2, _translate("MainWindow", "Kamada-Kawai"))
        self.network_combo.setItemText(3, _translate("MainWindow", "Planar"))
        self.network_combo.setItemText(4, _translate("MainWindow", "Spring"))
        self.species_combo.setItemText(0, _translate("MainWindow", "Choose species"))
        self.canvas_save_3.setText(_translate("MainWindow", "Save"))
        self.output_toolbar.setTabText(self.output_toolbar.indexOf(self.network_tab),
                                       _translate("MainWindow", "Network"))
        self.output_toolbar.setTabText(self.output_toolbar.indexOf(self.graph_tab),
                                       _translate("MainWindow", "Simulation plot"))
        self.text_output_save.setText(_translate("MainWindow", "Save"))
        self.output_toolbar.setTabText(self.output_toolbar.indexOf(self.text_output_tab),
                                       _translate("MainWindow", "Text output"))
        self.terminal.setTabText(self.terminal.indexOf(self.terminal_output),
                                 _translate("MainWindow", "Logging console"))
        self.terminal.setTabText(self.terminal.indexOf(self.terminal_error), _translate("MainWindow", "Error console"))

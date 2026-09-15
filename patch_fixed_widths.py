import re

with open("main.py", "r") as f:
    main_content = f.read()

# Lock profile_bar
main_content = main_content.replace("profile_bar.setMinimumWidth(170)", "profile_bar.setFixedWidth(240)")
main_content = main_content.replace("profile_bar.setMaximumWidth(280)", "")
main_content = main_content.replace("profile_bar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)", "profile_bar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)")

with open("main.py", "w") as f:
    f.write(main_content)

with open("analysis_ui.py", "r") as f:
    ana_content = f.read()

# Lock right_pane_wrapper
ana_content = ana_content.replace("self.right_pane_wrapper = QWidget()", "self.right_pane_wrapper = QWidget()\n        self.right_pane_wrapper.setFixedWidth(345)\n        self.right_pane_wrapper.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)")

with open("analysis_ui.py", "w") as f:
    f.write(ana_content)

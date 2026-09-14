import sys

with open('main.py', 'r') as f:
    content = f.read()
    
# 1. Rename tabs and hide measurement tab
old_tabs = """        self.btn_nav_meas = QPushButton(" Measurement")
        self.btn_nav_ana = QPushButton(" Analysis")"""
        
new_tabs = """        self.btn_nav_meas = QPushButton(" Measurement")
        self.btn_nav_meas.hide()
        self.btn_nav_ana = QPushButton(" Workspace")"""
content = content.replace(old_tabs, new_tabs)

# 2. Modify control_panel injection
old_bottom = """        # Container to add some top margin
        bottom_container = QVBoxLayout()
        bottom_container.setContentsMargins(0, 15, 0, 0)
        bottom_container.addWidget(control_panel)
        
        meas_layout.addLayout(bottom_container)"""

new_bottom = """        # Container to add some top margin
        bottom_container = QVBoxLayout()
        bottom_container.setContentsMargins(0, 15, 0, 0)
        bottom_container.addWidget(control_panel)
        
        # Merge into Analysis page instead of Measurement page
        # Hide the redundant dropdowns in the bottom bar since Analysis already has them
        self.cb_meas_target.hide()
        self.cb_meas_history.hide()
        
        if hasattr(self, 'page_ana'):
            self.page_ana.layout.addLayout(bottom_container)
        else:
            meas_layout.addLayout(bottom_container)"""
content = content.replace(old_bottom, new_bottom)

# 3. Fix Live RTA plotting to use the Analysis graph!
old_rta = """            if hasattr(self, 'live_rta_line') and self.live_rta_line is not None:
                try:
                    self.plot_widget.removeItem(self.live_rta_line)
                except Exception:
                    pass
            self.live_rta_line = self.plot_widget.plot(pen=pg.mkPen('#db2777', width=2), name="Live Seal")
            self.live_rta_line.show()"""

new_rta = """            # Plot to Analysis graph!
            target_plot = self.page_ana.plot_widget if hasattr(self, 'page_ana') else self.plot_widget
            if hasattr(self, 'live_rta_line') and self.live_rta_line is not None:
                try:
                    target_plot.removeItem(self.live_rta_line)
                except Exception:
                    pass
            self.live_rta_line = target_plot.plot(pen=pg.mkPen('#db2777', width=2), name="Live Seal")
            self.live_rta_line.show()"""
content = content.replace(old_rta, new_rta)

# 4. Make sure on_measurement_finished automatically switches to workspace
old_meas_finish = """        self.redraw_graph()
        ref_l = getattr(self, 'ref_mag_l', None)"""
new_meas_finish = """        self.redraw_graph()
        self.switch_workspace_tab(2)
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'graph_tabs'):
            self.page_ana.graph_tabs.setCurrentIndex(0)
        ref_l = getattr(self, 'ref_mag_l', None)"""
content = content.replace(old_meas_finish, new_meas_finish)

with open('main.py', 'w') as f:
    f.write(content)

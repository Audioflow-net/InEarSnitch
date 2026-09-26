import re

with open("main.py", "r") as f:
    content = f.read()

old_logic = """    def load_targets(self):
        # We populate the four combo boxes (2 in Meas, 2 in Ana)
        boxes_hist = [self.cb_meas_history, self.page_ana.cb_ana_history]
        boxes_tgt = [self.cb_meas_target, self.page_ana.cb_ana_target]
        
        for b in boxes_hist + boxes_tgt:
            b.blockSignals(True)
            b.clear()"""

new_logic = """    def load_targets(self):
        # We populate the four combo boxes (2 in Meas, 2 in Ana)
        boxes_hist = [self.cb_meas_history, self.page_ana.cb_ana_history]
        boxes_tgt = [self.cb_meas_target, self.page_ana.cb_ana_target]
        
        # Save current selections to restore them after clearing
        saved_hist = self.cb_meas_history.currentText() if hasattr(self, 'cb_meas_history') and self.cb_meas_history.count() > 0 else None
        saved_tgt = self.cb_meas_target.currentText() if hasattr(self, 'cb_meas_target') and self.cb_meas_target.count() > 0 else None
        
        for b in boxes_hist + boxes_tgt:
            b.blockSignals(True)
            b.clear()"""

content = content.replace(old_logic, new_logic)

old_restore = """        if len(sys.argv) > 1 and sys.argv[1].endswith('.csv'):
            self._apply_target_selection(sys.argv[1])"""

new_restore = """        # Restore selections
        if saved_hist and saved_hist != "No History Selected":
            idx = self.cb_meas_history.findText(saved_hist)
            if idx >= 0:
                for b in boxes_hist:
                    b.setCurrentIndex(idx)
        if saved_tgt and saved_tgt != "No Target Selected":
            idx = self.cb_meas_target.findText(saved_tgt)
            if idx >= 0:
                for b in boxes_tgt:
                    b.setCurrentIndex(idx)
                    
        for b in boxes_hist + boxes_tgt:
            b.blockSignals(False)

        if len(sys.argv) > 1 and sys.argv[1].endswith('.csv'):
            self._apply_target_selection(sys.argv[1])"""

content = content.replace(old_restore, new_restore)

with open("main.py", "w") as f:
    f.write(content)

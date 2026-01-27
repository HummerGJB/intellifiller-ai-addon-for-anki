from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, showWarning


from .settings_window_ui import Ui_SettingsWindow
from .config_manager import ConfigManager
from .backup_manager import BackupManager
from .data_request import test_connection
import json
import os


class ConnectionTestWorker(QThread):
    success = pyqtSignal(str)
    failure = pyqtSignal(str)

    def __init__(self, config, timeout):
        super().__init__()
        self.config = config
        self.timeout = timeout

    def run(self):
        try:
            provider = test_connection(self.config, timeout=self.timeout)
            self.success.emit(provider)
        except Exception as e:
            self.failure.emit(str(e))




class SettingsWindow(QDialog, Ui_SettingsWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.setWindowTitle('ChatGPT Settings')
        config = ConfigManager.get_full_config()
        self.setup_config(config)
        
        # Hide the old save button (keep it in layout but invisible)
        self.saveButton.setVisible(False)
        
        # Create standard button box
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        
        # Add OK and Cancel
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        
        # Add "Save" (Apply)
        self.applyButton = self.buttonBox.addButton("Save", QDialogButtonBox.ButtonRole.ApplyRole)
        
        # Add to the vertical layout at the bottom
        self.verticalLayout.addWidget(self.buttonBox)

        # Connect signals
        self.buttonBox.accepted.connect(self.on_ok_clicked)
        self.buttonBox.rejected.connect(self.on_cancel_clicked)
        self.applyButton.clicked.connect(self.on_apply_clicked)
        

        self.backupNowBtn.clicked.connect(self.trigger_manual_backup)
        
        # Connect API selection to stacked widget page
        self.selectedApi.currentIndexChanged.connect(self.stackedWidget.setCurrentIndex)
        # Set initial page based on config
        self.stackedWidget.setCurrentIndex(self.selectedApi.currentIndex())

        # Test Connection
        self.testConnectionButton.clicked.connect(self.on_test_connection_clicked)
        
        self.setup_password_fields()
        
        # Connect Backup Browse Buttons
        self.browseLocalPathBtn.clicked.connect(self.browse_local_path)
        self.browseExternalPathBtn.clicked.connect(self.browse_external_path)
        
        # Track initial state for unsaved changes detection
        # IMPORTANT: We capture this AFTER all UI setup is done, so get_current_config returns the true initial state
        self.original_config = json.dumps(self.get_current_config(), sort_keys=True)
        self.config_saved = False
        
        self.batchEnabled.toggled.connect(self.update_batch_ui_state)
        self._connection_test_worker = None

    def update_batch_ui_state(self, checked):
        self.batchSize.setEnabled(checked)
        self.batchDelay.setEnabled(checked)
        self.batchRandom.setEnabled(checked)
        self.randomDelayMin.setEnabled(checked and self.batchRandom.isChecked())
        self.randomDelayMax.setEnabled(checked and self.batchRandom.isChecked())

    def update_random_ui_state(self, checked):
        enabled = self.batchEnabled.isChecked() and checked
        self.randomDelayMin.setEnabled(enabled)
        self.randomDelayMax.setEnabled(enabled)

    def _set_test_button_state(self, enabled):
        self.testConnectionButton.setEnabled(enabled)
        self.testConnectionButton.setText("Test Connection" if enabled else "Testing...")

    def setup_password_fields(self):
        """Configures API key fields to be masked with a toggle button."""
        fields = [
            self.apiKey, 
            self.anthropicKey, 
            self.geminiKey, 
            self.openrouterKey, 
            self.customKey, 
            self.encryptionKey,
            self.backupPassword
        ]
        
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_eye = QIcon(os.path.join(addon_dir, 'eye.svg'))
        self.icon_eye_off = QIcon(os.path.join(addon_dir, 'eye-off.svg'))

        for field in fields:
            self._add_eye_toggle(field)

    def _add_eye_toggle(self, line_edit):
        line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Action to toggle visibility
        action = line_edit.addAction(self.icon_eye, QLineEdit.ActionPosition.TrailingPosition)
        
        def toggle():
            if line_edit.echoMode() == QLineEdit.EchoMode.Password:
                line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
                action.setIcon(self.icon_eye_off)
            else:
                line_edit.setEchoMode(QLineEdit.EchoMode.Password)
                action.setIcon(self.icon_eye)
        
        action.triggered.connect(toggle)

    def on_test_connection_clicked(self):
        config = self._build_test_config()
        validation_error = self._validate_test_config(config)
        if validation_error:
            showWarning(validation_error)
            return

        self._set_test_button_state(False)
        timeout = float(self.netTimeout.value())

        self._connection_test_worker = ConnectionTestWorker(config, timeout)
        self._connection_test_worker.success.connect(self._on_connection_test_success)
        self._connection_test_worker.failure.connect(self._on_connection_test_failure)
        self._connection_test_worker.finished.connect(self._on_connection_test_finished)
        self._connection_test_worker.start()

    def _on_connection_test_success(self, provider_label):
        showInfo(f"Connection succeeded using {provider_label}.")

    def _on_connection_test_failure(self, error_message):
        showWarning(f"Connection failed.\n\n{error_message}")

    def _on_connection_test_finished(self):
        self._set_test_button_state(True)
        self._connection_test_worker = None

    def _build_test_config(self):
        return {
            "selectedApi": self.selectedApi.currentData(),
            "apiKey": self.apiKey.text().strip(),
            "openaiModel": self.openaiModel.text().strip(),
            "anthropicKey": self.anthropicKey.text().strip(),
            "anthropicModel": self.anthropicModel.text().strip(),
            "geminiKey": self.geminiKey.text().strip(),
            "geminiModel": self.geminiModel.text().strip(),
            "openrouterKey": self.openrouterKey.text().strip(),
            "openrouterModel": self.openrouterModel.text().strip(),
            "customUrl": self.customUrl.text().strip(),
            "customKey": self.customKey.text().strip(),
            "customModel": self.customModel.text().strip(),
        }

    def _validate_test_config(self, config):
        selected = config.get("selectedApi", "openai")

        if selected == "openai":
            if not config.get("apiKey"):
                return "OpenAI API key is required to test the connection."
            return None

        if selected == "anthropic":
            if not config.get("anthropicKey"):
                return "Anthropic API key is required to test the connection."
            return None

        if selected == "gemini":
            if not config.get("geminiKey"):
                return "Google Gemini API key is required to test the connection."
            return None

        if selected == "openrouter":
            if not config.get("openrouterKey"):
                return "OpenRouter API key is required to test the connection."
            return None

        if selected == "custom":
            if not config.get("customUrl"):
                return "OpenAI compatible base URL is required to test the connection."
            if not config.get("customKey"):
                return "OpenAI compatible API key is required to test the connection."
            return None

        return "Unknown API selection. Please choose a provider and try again."

    def setWindowSize(self):
        screen_size = QGuiApplication.primaryScreen().geometry()
        self.resize(screen_size.width() * 0.8, screen_size.height() * 0.8)

    def setup_config(self, config):
        self.apiKey.setText(config.get("apiKey", ""))
        self.openaiModel.setText(config.get("openaiModel", ""))
        self.anthropicKey.setText(config.get("anthropicKey", ""))
        self.anthropicModel.setText(config.get("anthropicModel", ""))
        self.geminiKey.setText(config.get("geminiKey", ""))
        self.geminiModel.setText(config.get("geminiModel", ""))
        self.openrouterKey.setText(config.get("openrouterKey", ""))
        self.openrouterModel.setText(config.get("openrouterModel", ""))
        self.customUrl.setText(config.get("customUrl", ""))
        self.customKey.setText(config.get("customKey", ""))
        self.customModel.setText(config.get("customModel", ""))
        
        # Select correct API based on stored key (data)
        index = self.selectedApi.findData(config.get("selectedApi", "openai"))
        if index >= 0:
            self.selectedApi.setCurrentIndex(index)
        
        # Ensure correct stack page is shown after setting text
        self.stackedWidget.setCurrentIndex(self.selectedApi.currentIndex())
        
        self.emulate.setCurrentText(config.get("emulate", "no"))
        self.overwriteField.setChecked(config.get("overwriteField", False))
        self.flatMenu.setChecked(config.get("flatMenu", False))
        self.maxFavorites.setValue(config.get("maxFavorites", 3))
        self.netTimeout.setValue(config.get("netTimeout", 10))
        # Default to True (Security by Default)
        self.obfuscateCreds.setChecked(config.get("obfuscateCreds", True))
        self.encryptionKey.setText(config.get("encryptionKey", ""))
        
        # Batch Processing
        batch_config = config.get("batchProcessing", {})
        self.batchEnabled.setChecked(batch_config.get("enabled", True))
        self.batchSize.setValue(batch_config.get("batchSize", 20))
        self.batchDelay.setValue(batch_config.get("batchDelay", 5))
        self.batchRandom.setChecked(batch_config.get("randomDelay", True))
        self.randomDelayMin.setValue(batch_config.get("randomDelayMin", 0))
        self.randomDelayMax.setValue(batch_config.get("randomDelayMax", 10))
        
        # Connect additional signal for batchRandom toggle
        self.batchRandom.toggled.connect(self.update_random_ui_state)
        
        self.update_batch_ui_state(self.batchEnabled.isChecked())
        
        self.pipelinesList.currentRowChanged.connect(self.display_pipeline_details)
        self.addPipelineButton.clicked.connect(self.add_new_pipeline)
        self.removePipelineButton.clicked.connect(self.remove_selected_pipeline)
        self.pipelineName.textChanged.connect(self.update_current_pipeline_name)
        self.pipelinePinnedCheckbox.clicked.connect(self.update_current_pipeline_pinned)
        self.addPromptToPipelineButton.clicked.connect(self.add_prompt_to_pipeline)
        self.removePromptFromPipelineButton.clicked.connect(self.remove_prompt_from_pipeline)

        self.pipelines = config.get("pipelines", [])
        self.refresh_pipelines_list()

        # Prompts Setup
        self.promptsList.currentRowChanged.connect(self.display_prompt_details)
        self.addPromptButton.clicked.connect(self.add_new_prompt)
        self.removePromptButton.clicked.connect(self.remove_selected_prompt)
        
        # Connect Prompt Detail Change Signals
        self.promptName.textChanged.connect(self.update_current_prompt_name)
        self.promptPinnedCheckbox.clicked.connect(self.update_current_prompt_pinned)
        self.promptResponseFormat.currentTextChanged.connect(self.update_current_prompt_format)
        self.promptTargetField.textChanged.connect(self.update_current_prompt_target)
        self.promptProviderOverride.currentIndexChanged.connect(self.update_current_prompt_provider)
        self.promptModelOverride.textChanged.connect(self.update_current_prompt_model)
        self.promptSystemPrompt.textChanged.connect(self.update_current_prompt_system)
        self.promptTemperature.valueChanged.connect(self.update_current_prompt_temperature)
        self.promptMaxTokens.valueChanged.connect(self.update_current_prompt_max_tokens)
        self.promptFieldMapping.textChanged.connect(self.update_current_prompt_mapping)
        self.promptText.textChanged.connect(self.update_current_prompt_text)

        self.prompts = config.get("prompts", [])
        self.refresh_prompts_list()

        # Backup Settings
        backup = config.get("backup", {})
        self.backupEnabled.setChecked(backup.get("enabled", False))
        self.backupInterval.setValue(backup.get("intervalMinutes", 10))
        self.backupOnSettingsOpen.setChecked(backup.get("backupOnSettingsOpen", True))
        try:
            import pyzipper
            has_pyzipper = True
        except ImportError:
            has_pyzipper = False

        self.backupPassword.setText(backup.get("zipPassword", ""))
        if has_pyzipper:
            self.backupPassword.setPlaceholderText("Enter password for AES-256 encryption")
            self.backupPassword.setToolTip("Backups will be encrypted with strong AES-256.")
        else:
             self.backupPassword.setPlaceholderText("Encryption unavailable (missing pyzipper)")
             self.backupPassword.setToolTip("WARNING: 'pyzipper' module is missing. Password protection is disabled.\nRun scripts/setup_vendor.py to enable.")
        self.backupLocalPath.setText(backup.get("localPath", ""))
        self.backupExternalPath.setText(backup.get("externalPath", ""))
        
        self.keepTenMin.setValue(backup.get("keepTenMin", 6))
        self.keepHourly.setValue(backup.get("keepHourly", 24))
        self.keepDaily.setValue(backup.get("keepDaily", 30))
        self.keepMonthly.setValue(backup.get("keepMonthly", 12))
        self.keepYearly.setValue(backup.get("keepYearly", 5))


    def refresh_pipelines_list(self):
        self.pipelinesList.clear()
        for pipeline in self.pipelines:
            self.pipelinesList.addItem(pipeline["pipelineName"])

    def display_pipeline_details(self, row):
        if row < 0 or row >= len(self.pipelines):
            self.pipelineDetailsGroup.setEnabled(False)
            self.pipelineName.clear()
            self.pipelinePinnedCheckbox.setChecked(False)
            self.pipelinePromptsList.clear()
            return

        self.pipelineDetailsGroup.setEnabled(True)
        pipeline = self.pipelines[row]
        self.pipelineName.setText(pipeline["pipelineName"])
        self.pipelinePinnedCheckbox.setChecked(pipeline.get("pinned", False))
        
        self.pipelinePromptsList.clear()
        for prompt_name in pipeline["prompts"]:
            self.pipelinePromptsList.addItem(prompt_name)

    def add_new_pipeline(self):
        new_pipeline = {"pipelineName": "New Pipeline", "prompts": [], "pinned": False}
        self.pipelines.append(new_pipeline)
        self.refresh_pipelines_list()
        self.pipelinesList.setCurrentRow(len(self.pipelines) - 1)

    def remove_selected_pipeline(self):
        row = self.pipelinesList.currentRow()
        if row >= 0:
            del self.pipelines[row]
            self.refresh_pipelines_list()

    def update_current_pipeline_name(self, text):
        row = self.pipelinesList.currentRow()
        if row >= 0:
            self.pipelines[row]["pipelineName"] = text
            item = self.pipelinesList.item(row)
            item.setText(text)

    def update_current_pipeline_pinned(self):
        row = self.pipelinesList.currentRow()
        if row >= 0:
            self.pipelines[row]["pinned"] = self.pipelinePinnedCheckbox.isChecked()

    def add_prompt_to_pipeline(self):
        row = self.pipelinesList.currentRow()
        if row < 0:
            return

        # Get list of all available prompts
        available_prompts = [p.get("promptName", "Unnamed") for p in self.prompts]
        if not available_prompts:
            showInfo("No prompts available to add.")
            return

        prompt_name, ok = QInputDialog.getItem(
            self, "Select Prompt", "Choose a prompt to add:", available_prompts, 0, False
        )
        if ok and prompt_name:
            self.pipelines[row]["prompts"].append(prompt_name)
            self.pipelinePromptsList.addItem(prompt_name)

    def remove_prompt_from_pipeline(self):
        pipeline_row = self.pipelinesList.currentRow()
        prompt_row = self.pipelinePromptsList.currentRow()
        if pipeline_row >= 0 and prompt_row >= 0:
            del self.pipelines[pipeline_row]["prompts"][prompt_row]
            self.pipelinePromptsList.takeItem(prompt_row)


    def refresh_prompts_list(self):
        current_row = self.promptsList.currentRow()
        self.promptsList.clear()
        for prompt in self.prompts:
            self.promptsList.addItem(prompt.get("promptName", "Unnamed Prompt"))
        
        if current_row >= 0 and current_row < len(self.prompts):
            self.promptsList.setCurrentRow(current_row)

    def display_prompt_details(self, row):
        # Block signals to prevent update feedback loops when populating fields
        self.promptName.blockSignals(True)
        self.promptPinnedCheckbox.blockSignals(True)
        self.promptResponseFormat.blockSignals(True)
        self.promptTargetField.blockSignals(True)
        self.promptProviderOverride.blockSignals(True)
        self.promptModelOverride.blockSignals(True)
        self.promptSystemPrompt.blockSignals(True)
        self.promptTemperature.blockSignals(True)
        self.promptMaxTokens.blockSignals(True)
        self.promptFieldMapping.blockSignals(True)
        self.promptText.blockSignals(True)

        if row < 0 or row >= len(self.prompts):
            self.promptDetailsGroup.setEnabled(False)
            self.promptName.clear()
            self.promptPinnedCheckbox.setChecked(False)
            self.promptResponseFormat.setCurrentIndex(0) # Text
            self.promptTargetField.clear()
            self.promptProviderOverride.setCurrentIndex(0)
            self.promptModelOverride.clear()
            self.promptSystemPrompt.clear()
            self.promptTemperature.setValue(-1.0)
            self.promptMaxTokens.setValue(-1)
            self.promptFieldMapping.clear()
            self.promptText.clear()
        else:
            self.promptDetailsGroup.setEnabled(True)
            prompt = self.prompts[row]
            
            self.promptName.setText(prompt.get("promptName", ""))
            self.promptPinnedCheckbox.setChecked(prompt.get("pinned", False))
            
            fmt = prompt.get("responseFormat", "text")
            self.promptResponseFormat.setCurrentText("JSON" if fmt == "json" else "Text")
            self.update_prompt_ui_visibility(fmt)

            self.promptTargetField.setText(prompt.get("targetField", ""))

            provider_override = prompt.get("providerOverride", "")
            provider_index = self.promptProviderOverride.findData(provider_override)
            if provider_index == -1:
                provider_index = 0
            self.promptProviderOverride.setCurrentIndex(provider_index)
            self.promptModelOverride.setText(prompt.get("modelOverride", ""))
            self.promptSystemPrompt.setPlainText(prompt.get("systemPrompt", ""))
            temperature = prompt.get("temperature")
            self.promptTemperature.setValue(temperature if isinstance(temperature, (int, float)) else -1.0)
            max_tokens = prompt.get("maxTokens")
            self.promptMaxTokens.setValue(max_tokens if isinstance(max_tokens, int) else -1)
            
            mapping = prompt.get("fieldMapping", {})
            mapping_text = ""
            for k, v in mapping.items():
                mapping_text += f"{k}: {v}\n"
            self.promptFieldMapping.setPlainText(mapping_text.strip())
            
            self.promptText.setPlainText(prompt.get("prompt", ""))

        self.promptName.blockSignals(False)
        self.promptPinnedCheckbox.blockSignals(False)
        self.promptResponseFormat.blockSignals(False)
        self.promptTargetField.blockSignals(False)
        self.promptProviderOverride.blockSignals(False)
        self.promptModelOverride.blockSignals(False)
        self.promptSystemPrompt.blockSignals(False)
        self.promptTemperature.blockSignals(False)
        self.promptMaxTokens.blockSignals(False)
        self.promptFieldMapping.blockSignals(False)
        self.promptText.blockSignals(False)

    def update_prompt_ui_visibility(self, fmt):
        is_json = (fmt == "json")
        self.labelPromptTarget.setVisible(not is_json)
        self.promptTargetField.setVisible(not is_json)
        self.labelPromptMapping.setVisible(is_json)
        self.promptFieldMapping.setVisible(is_json)

    def add_new_prompt(self):
        new_prompt = {
            "promptName": "New Prompt",
            "prompt": "",
            "targetField": "",
            "pinned": False,
            "responseFormat": "text",
            "fieldMapping": {}
        }
        self.prompts.append(new_prompt)
        self.refresh_prompts_list()
        self.promptsList.setCurrentRow(len(self.prompts) - 1)
        self.promptName.setFocus()
        self.promptName.selectAll()

    def remove_selected_prompt(self):
        row = self.promptsList.currentRow()
        if row >= 0:
            del self.prompts[row]
            self.refresh_prompts_list()

    def update_current_prompt_name(self, text):
        row = self.promptsList.currentRow()
        if row >= 0:
            self.prompts[row]["promptName"] = text
            self.promptsList.item(row).setText(text or "Unnamed Prompt")

    def update_current_prompt_pinned(self):
        row = self.promptsList.currentRow()
        if row >= 0:
            self.prompts[row]["pinned"] = self.promptPinnedCheckbox.isChecked()

    def update_current_prompt_format(self, text):
        row = self.promptsList.currentRow()
        if row >= 0:
            fmt = "json" if text == "JSON" else "text"
            self.prompts[row]["responseFormat"] = fmt
            self.update_prompt_ui_visibility(fmt)

    def update_current_prompt_target(self, text):
        row = self.promptsList.currentRow()
        if row >= 0:
            self.prompts[row]["targetField"] = text

    def update_current_prompt_provider(self):
        row = self.promptsList.currentRow()
        if row >= 0:
            value = self.promptProviderOverride.currentData()
            if value:
                self.prompts[row]["providerOverride"] = value
            else:
                self.prompts[row].pop("providerOverride", None)

    def update_current_prompt_model(self, text):
        row = self.promptsList.currentRow()
        if row >= 0:
            text = text.strip()
            if text:
                self.prompts[row]["modelOverride"] = text
            else:
                self.prompts[row].pop("modelOverride", None)

    def update_current_prompt_system(self):
        row = self.promptsList.currentRow()
        if row >= 0:
            text = self.promptSystemPrompt.toPlainText().strip()
            if text:
                self.prompts[row]["systemPrompt"] = text
            else:
                self.prompts[row].pop("systemPrompt", None)

    def update_current_prompt_temperature(self, value):
        row = self.promptsList.currentRow()
        if row >= 0:
            if value <= -1.0:
                self.prompts[row].pop("temperature", None)
            else:
                self.prompts[row]["temperature"] = float(value)

    def update_current_prompt_max_tokens(self, value):
        row = self.promptsList.currentRow()
        if row >= 0:
            if value <= -1:
                self.prompts[row].pop("maxTokens", None)
            else:
                self.prompts[row]["maxTokens"] = int(value)

    def update_current_prompt_mapping(self):
        row = self.promptsList.currentRow()
        if row >= 0:
            text = self.promptFieldMapping.toPlainText()
            mapping = {}
            lines = text.split('\n')
            for line in lines:
                if ':' in line:
                    k, v = line.split(':', 1)
                    mapping[k.strip()] = v.strip()
            self.prompts[row]["fieldMapping"] = mapping

    def update_current_prompt_text(self):
        row = self.promptsList.currentRow()
        if row >= 0:
            self.prompts[row]["prompt"] = self.promptText.toPlainText()

    def _save_settings_logic(self):
        """Internal logic to save settings without closing."""
        full_config = self.get_current_config()
        
        # 1. Credentials
        cred_keys = [
            "apiKey", "openaiModel", 
            "anthropicKey", "anthropicModel", 
            "geminiKey", "geminiModel", 
            "openrouterKey", "openrouterModel", 
            "customUrl", "customKey", "customModel"
        ]
        credentials = {k: full_config.get(k, "") for k in cred_keys}
        
        # Add Backup Password to credentials (mapped)
        backup_pass = full_config.get('backup', {}).get('zipPassword', "")
        credentials["backupZipPassword"] = backup_pass
        
        # Pull obfuscation setting directly from UI since it's part of 'settings', not 'credentials'
        should_obfuscate = self.obfuscateCreds.isChecked()
        custom_key = self.encryptionKey.text()
        
        # Save credentials using the NEW key (re-encryption happens here automatically)
        ConfigManager.save_credentials(credentials, key=custom_key, obfuscate=should_obfuscate)

        # 2. Prompts
        # Capture state BEFORE saving to know what to delete later
        existing_prompts = ConfigManager.list_prompts()
        existing_names = set(p['promptName'] for p in existing_prompts)
        new_names = set(p['promptName'] for p in full_config['prompts'])
        
        # Save all current prompts FIRST (Safety Fix)
        for prompt in full_config['prompts']:
            ConfigManager.save_prompt(prompt)

        # Remove obsolete files (Safe to do now)
        for name in existing_names:
            if name not in new_names:
                ConfigManager.delete_prompt_file(name)

        # 3. Settings (exclude credentials and prompts)
        settings = {}
        for k, v in full_config.items():
            if k not in cred_keys and k != "prompts":
                settings[k] = v
        
        # SECURITY STRIP: Remove password from backup settings before saving to plain text
        if 'backup' in settings and 'zipPassword' in settings['backup']:
            settings['backup']['zipPassword'] = ""
            
        ConfigManager.save_settings(settings)
        
        # Update internal tracking
        self.original_config = json.dumps(full_config, sort_keys=True)
        self.config_saved = True

    def on_ok_clicked(self):
        self._save_settings_logic()
        self.accept()

    def on_apply_clicked(self):
        self._save_settings_logic()
        showInfo("Configuration saved.")

    def on_cancel_clicked(self):
        self.reject()

    def get_current_config(self):
        # Start with existing settings to preserve hidden fields (like 'history')
        config = ConfigManager.load_settings()
        
        # Overlay UI values
        config["openaiModel"] = self.openaiModel.text()
        config["apiKey"] = self.apiKey.text()
        config["anthropicKey"] = self.anthropicKey.text()
        config["anthropicModel"] = self.anthropicModel.text()
        config["geminiKey"] = self.geminiKey.text()
        config["geminiModel"] = self.geminiModel.text()
        config["openrouterKey"] = self.openrouterKey.text()
        config["openrouterModel"] = self.openrouterModel.text()
        config["customUrl"] = self.customUrl.text()
        config["customKey"] = self.customKey.text()
        config["customModel"] = self.customModel.text()
        config["selectedApi"] = self.selectedApi.currentData()
        config["emulate"] = self.emulate.currentText()
        config["overwriteField"] = self.overwriteField.isChecked()
        config["flatMenu"] = self.flatMenu.isChecked()
        config["maxFavorites"] = self.maxFavorites.value()
        config["netTimeout"] = self.netTimeout.value()
        config["obfuscateCreds"] = self.obfuscateCreds.isChecked()
        config["encryptionKey"] = self.encryptionKey.text()
        
        config["batchProcessing"] = {
            "enabled": self.batchEnabled.isChecked(),
            "batchSize": self.batchSize.value(),
            "batchDelay": self.batchDelay.value(),
            "randomDelay": self.batchRandom.isChecked(),
            "randomDelayMin": self.randomDelayMin.value(),
            "randomDelayMax": self.randomDelayMax.value()
        }
        
        config["prompts"] = self.prompts
        
        config["pipelines"] = self.pipelines
        
        # Backup Settings
        config["backup"] = {
            "enabled": self.backupEnabled.isChecked(),
            "intervalMinutes": self.backupInterval.value(),
            "backupOnSettingsOpen": self.backupOnSettingsOpen.isChecked(),
            "zipPassword": self.backupPassword.text(),
            "localPath": self.backupLocalPath.text(),
            "externalPath": self.backupExternalPath.text(),
            "keepTenMin": self.keepTenMin.value(),
            "keepHourly": self.keepHourly.value(),
            "keepDaily": self.keepDaily.value(),
            "keepMonthly": self.keepMonthly.value(),
            "keepYearly": self.keepYearly.value()
        }
        
        return config

    def browse_local_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Local Backup Directory", self.backupLocalPath.text())
        if directory:
            self.backupLocalPath.setText(directory)

    def browse_external_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select External Backup Directory", self.backupExternalPath.text())
        if directory:
            self.backupExternalPath.setText(directory)


    def trigger_manual_backup(self):
        # Save current settings to memory
        temp_config = self.get_current_config()
        # Persist to disk so BackupManager sees them
        ConfigManager.save_settings(temp_config)
        
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        bm = BackupManager(ConfigManager, addon_dir)
        try:
            bm.perform_backup(force=True, backup_type='manual')
            showInfo("Backup completed successfully.\n\nCheck your configured local/external folders.")
        except Exception as e:
            showInfo(f"Backup failed: {str(e)}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_S and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self._save_settings_logic()
            showInfo("Configuration saved.")
        else:
            super().keyPressEvent(event)

    def reject(self):
        """Handle Esc key and Cancel button by invoking default Close behavior."""
        self.close()

    def closeEvent(self, event):
        if self.config_saved:
            event.accept()
            return

        current_config = self.get_current_config()
        current_config_str = json.dumps(current_config, sort_keys=True)
        
        # Compare current state with the captured state at open
        if current_config_str != self.original_config:
            reply = QMessageBox.question(
                self, 
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them before closing?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self._save_settings_logic()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

# -*- coding: utf-8 -*-

from aqt import qt
QtCore = qt
QtGui = qt
QtWidgets = qt

class Ui_SettingsWindow(object):
    def setupUi(self, SettingsWindow):
        SettingsWindow.setObjectName("SettingsWindow")
        SettingsWindow.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        SettingsWindow.resize(600, 500)
        
        self.verticalLayout = QtWidgets.QVBoxLayout(SettingsWindow)
        self.verticalLayout.setObjectName("verticalLayout")

        self.tabWidget = QtWidgets.QTabWidget(SettingsWindow)
        self.tabWidget.setObjectName("tabWidget")
        
        # --- API Tab ---
        self.tabApi = QtWidgets.QWidget()
        self.tabApi.setObjectName("tabApi")
        self.tabApiLayout = QtWidgets.QVBoxLayout(self.tabApi)
        
        # 1. API Selector at the top
        self.labelSelectedApi = QtWidgets.QLabel(self.tabApi)
        self.selectedApi = QtWidgets.QComboBox(self.tabApi)
        self.selectedApi.addItem("OpenAI", "openai")
        self.selectedApi.addItem("Anthropic", "anthropic")
        self.selectedApi.addItem("Google Gemini", "gemini")
        self.selectedApi.addItem("OpenRouter", "openrouter")
        self.selectedApi.addItem("OpenAI Compatible", "custom")
        
        self.apiSelectorLayout = QtWidgets.QFormLayout()
        self.apiSelectorLayout.addRow(self.labelSelectedApi, self.selectedApi)
        self.tabApiLayout.addLayout(self.apiSelectorLayout)
        
        # 2. Stacked Widget for Provider specific fields
        self.stackedWidget = QtWidgets.QStackedWidget(self.tabApi)
        self.tabApiLayout.addWidget(self.stackedWidget)
        
        # Page 0: OpenAI
        self.pageOpenai = QtWidgets.QWidget()
        self.pageOpenaiLayout = QtWidgets.QFormLayout(self.pageOpenai)
        self.labelApiKey = QtWidgets.QLabel(self.pageOpenai)
        self.apiKey = QtWidgets.QLineEdit(self.pageOpenai)
        self.pageOpenaiLayout.addRow(self.labelApiKey, self.apiKey)
        self.labelOpenaiModel = QtWidgets.QLabel(self.pageOpenai)
        self.openaiModel = QtWidgets.QLineEdit(self.pageOpenai)
        self.pageOpenaiLayout.addRow(self.labelOpenaiModel, self.openaiModel)
        self.stackedWidget.addWidget(self.pageOpenai)
        
        # Page 1: Anthropic
        self.pageAnthropic = QtWidgets.QWidget()
        self.pageAnthropicLayout = QtWidgets.QFormLayout(self.pageAnthropic)
        self.labelAnthropicKey = QtWidgets.QLabel(self.pageAnthropic)
        self.anthropicKey = QtWidgets.QLineEdit(self.pageAnthropic)
        self.pageAnthropicLayout.addRow(self.labelAnthropicKey, self.anthropicKey)
        self.labelAnthropicModel = QtWidgets.QLabel(self.pageAnthropic)
        self.anthropicModel = QtWidgets.QLineEdit(self.pageAnthropic)
        self.pageAnthropicLayout.addRow(self.labelAnthropicModel, self.anthropicModel)
        self.stackedWidget.addWidget(self.pageAnthropic)
        
        # Page 2: Gemini
        self.pageGemini = QtWidgets.QWidget()
        self.pageGeminiLayout = QtWidgets.QFormLayout(self.pageGemini)
        self.labelGeminiKey = QtWidgets.QLabel(self.pageGemini)
        self.geminiKey = QtWidgets.QLineEdit(self.pageGemini)
        self.pageGeminiLayout.addRow(self.labelGeminiKey, self.geminiKey)
        self.labelGeminiModel = QtWidgets.QLabel(self.pageGemini)
        self.geminiModel = QtWidgets.QLineEdit(self.pageGemini)
        self.pageGeminiLayout.addRow(self.labelGeminiModel, self.geminiModel)
        self.stackedWidget.addWidget(self.pageGemini)
        
        # Page 3: OpenRouter
        self.pageOpenrouter = QtWidgets.QWidget()
        self.pageOpenrouterLayout = QtWidgets.QFormLayout(self.pageOpenrouter)
        self.labelOpenrouterKey = QtWidgets.QLabel(self.pageOpenrouter)
        self.openrouterKey = QtWidgets.QLineEdit(self.pageOpenrouter)
        self.pageOpenrouterLayout.addRow(self.labelOpenrouterKey, self.openrouterKey)
        self.labelOpenrouterModel = QtWidgets.QLabel(self.pageOpenrouter)
        self.openrouterModel = QtWidgets.QLineEdit(self.pageOpenrouter)
        self.pageOpenrouterLayout.addRow(self.labelOpenrouterModel, self.openrouterModel)
        self.stackedWidget.addWidget(self.pageOpenrouter)
        
        # Page 4: Custom
        self.pageCustom = QtWidgets.QWidget()
        self.pageCustomLayout = QtWidgets.QFormLayout(self.pageCustom)
        self.labelCustomUrl = QtWidgets.QLabel(self.pageCustom)
        self.customUrl = QtWidgets.QLineEdit(self.pageCustom)
        self.pageCustomLayout.addRow(self.labelCustomUrl, self.customUrl)
        self.labelCustomKey = QtWidgets.QLabel(self.pageCustom)
        self.customKey = QtWidgets.QLineEdit(self.pageCustom)
        self.pageCustomLayout.addRow(self.labelCustomKey, self.customKey)
        self.labelCustomModel = QtWidgets.QLabel(self.pageCustom)
        self.customModel = QtWidgets.QLineEdit(self.pageCustom)
        self.pageCustomLayout.addRow(self.labelCustomModel, self.customModel)
        self.stackedWidget.addWidget(self.pageCustom)

        # Test Connection button (applies to the selected provider)
        self.testConnectionLayout = QtWidgets.QHBoxLayout()
        self.testConnectionButton = QtWidgets.QPushButton(self.tabApi)
        self.testConnectionButton.setObjectName("testConnectionButton")
        self.testConnectionLayout.addWidget(self.testConnectionButton)
        self.testConnectionLayout.addStretch()
        self.tabApiLayout.addLayout(self.testConnectionLayout)

        # Emulation (Outside stack, always visible)
        self.emulationLayout = QtWidgets.QFormLayout()
        self.labelEmulate = QtWidgets.QLabel(self.tabApi)
        self.emulate = QtWidgets.QComboBox(self.tabApi)
        self.emulate.addItems(["yes", "no"])
        self.emulationLayout.addRow(self.labelEmulate, self.emulate)
        
        self.overwriteFieldLabel = QtWidgets.QLabel(self.tabApi)
        self.overwriteField = QtWidgets.QCheckBox(self.tabApi)
        self.emulationLayout.addRow(self.overwriteFieldLabel, self.overwriteField)
        
        self.flatMenuLabel = QtWidgets.QLabel(self.tabApi)
        self.flatMenu = QtWidgets.QCheckBox(self.tabApi)
        self.emulationLayout.addRow(self.flatMenuLabel, self.flatMenu)
        
        self.labelMaxFavorites = QtWidgets.QLabel(self.tabApi)
        self.maxFavorites = QtWidgets.QSpinBox(self.tabApi)
        self.maxFavorites.setMinimum(0)
        self.maxFavorites.setMaximum(10)
        self.emulationLayout.addRow(self.labelMaxFavorites, self.maxFavorites)

        self.labelObfuscate = QtWidgets.QLabel(self.tabApi)
        self.obfuscateCreds = QtWidgets.QCheckBox(self.tabApi)
        self.emulationLayout.addRow(self.labelObfuscate, self.obfuscateCreds)

        self.labelEncryptionKey = QtWidgets.QLabel(self.tabApi)
        self.encryptionKey = QtWidgets.QLineEdit(self.tabApi)
        self.encryptionKey.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.emulationLayout.addRow(self.labelEncryptionKey, self.encryptionKey)

        self.labelNetTimeout = QtWidgets.QLabel(self.tabApi)
        self.netTimeout = QtWidgets.QSpinBox(self.tabApi)
        self.netTimeout.setRange(5, 300)
        self.netTimeout.setSuffix(" sec")
        self.emulationLayout.addRow(self.labelNetTimeout, self.netTimeout)
        
        self.tabApiLayout.addLayout(self.emulationLayout)
        
        # Batch Processing
        self.batchGroup = QtWidgets.QGroupBox("Batch Processing", self.tabApi)
        self.batchLayout = QtWidgets.QFormLayout(self.batchGroup)
        
        self.batchEnabled = QtWidgets.QCheckBox(self.batchGroup)
        self.batchLayout.addRow(QtWidgets.QLabel("Enable Batch Processing:", self.batchGroup), self.batchEnabled)
        
        self.batchSize = QtWidgets.QSpinBox(self.batchGroup)
        self.batchSize.setRange(1, 1000)
        self.batchLayout.addRow(QtWidgets.QLabel("Batch Size (Notes):", self.batchGroup), self.batchSize)
        
        self.batchDelay = QtWidgets.QSpinBox(self.batchGroup)
        self.batchDelay.setSuffix(" sec")
        self.batchLayout.addRow(QtWidgets.QLabel("Delay between batches:", self.batchGroup), self.batchDelay)

        self.batchRandom = QtWidgets.QCheckBox(self.batchGroup)
        self.batchLayout.addRow(QtWidgets.QLabel("Enable Random Delay:", self.batchGroup), self.batchRandom)

        self.randomDelayMin = QtWidgets.QSpinBox(self.batchGroup)
        self.randomDelayMin.setRange(0, 3600)
        self.randomDelayMin.setSuffix(" sec")
        self.batchLayout.addRow(QtWidgets.QLabel("Min Random Delay:", self.batchGroup), self.randomDelayMin)

        self.randomDelayMax = QtWidgets.QSpinBox(self.batchGroup)
        self.randomDelayMax.setRange(0, 3600)
        self.randomDelayMax.setSuffix(" sec")
        self.batchLayout.addRow(QtWidgets.QLabel("Max Random Delay:", self.batchGroup), self.randomDelayMax)
        
        self.tabApiLayout.addWidget(self.batchGroup)
        
        # Spacer to push everything up
        self.tabApiLayout.addStretch()

        self.tabWidget.addTab(self.tabApi, "")

        # --- Prompts Tab ---
        self.tabPrompts = QtWidgets.QWidget()
        self.tabPrompts.setObjectName("tabPrompts")
        self.tabPromptsLayout = QtWidgets.QHBoxLayout(self.tabPrompts)
        
        # Left: List of Prompts
        self.promptsListLayout = QtWidgets.QVBoxLayout()
        self.promptsList = QtWidgets.QListWidget(self.tabPrompts)
        self.promptsListLayout.addWidget(self.promptsList)
        
        self.addPromptButton = QtWidgets.QPushButton(self.tabPrompts)
        self.promptsListLayout.addWidget(self.addPromptButton)
        self.removePromptButton = QtWidgets.QPushButton(self.tabPrompts)
        self.promptsListLayout.addWidget(self.removePromptButton)
        
        self.tabPromptsLayout.addLayout(self.promptsListLayout, 1)

        # Right: Prompt Details
        self.promptDetailsGroup = QtWidgets.QGroupBox("Prompt Details", self.tabPrompts)
        self.promptDetailsGroup.setEnabled(False)
        self.promptDetailsLayout = QtWidgets.QVBoxLayout(self.promptDetailsGroup)

        # Prompt Name
        self.promptNameLayout = QtWidgets.QHBoxLayout()
        self.labelPromptName = QtWidgets.QLabel("Name:", self.promptDetailsGroup)
        self.promptName = QtWidgets.QLineEdit(self.promptDetailsGroup)
        self.promptNameLayout.addWidget(self.labelPromptName)
        self.promptNameLayout.addWidget(self.promptName)
        self.promptDetailsLayout.addLayout(self.promptNameLayout)

        self.promptPinnedCheckbox = QtWidgets.QCheckBox("Pin to Menu", self.promptDetailsGroup)
        self.promptDetailsLayout.addWidget(self.promptPinnedCheckbox)
        
        # Response Format
        self.promptFormatLayout = QtWidgets.QHBoxLayout()
        self.labelPromptFormat = QtWidgets.QLabel("Response Format:", self.promptDetailsGroup)
        self.promptResponseFormat = QtWidgets.QComboBox(self.promptDetailsGroup)
        self.promptResponseFormat.addItems(["Text", "JSON"])
        self.promptFormatLayout.addWidget(self.labelPromptFormat)
        self.promptFormatLayout.addWidget(self.promptResponseFormat)
        self.promptFormatLayout.addStretch()
        self.promptDetailsLayout.addLayout(self.promptFormatLayout)

        # Target Field (Text Mode)
        self.promptTargetLayout = QtWidgets.QHBoxLayout()
        self.labelPromptTarget = QtWidgets.QLabel("Target Field:", self.promptDetailsGroup)
        self.promptTargetField = QtWidgets.QLineEdit(self.promptDetailsGroup)
        self.promptTargetLayout.addWidget(self.labelPromptTarget)
        self.promptTargetLayout.addWidget(self.promptTargetField)
        self.promptDetailsLayout.addLayout(self.promptTargetLayout)

        # Provider Override
        self.promptProviderLayout = QtWidgets.QHBoxLayout()
        self.labelPromptProvider = QtWidgets.QLabel("Provider Override:", self.promptDetailsGroup)
        self.promptProviderOverride = QtWidgets.QComboBox(self.promptDetailsGroup)
        self.promptProviderOverride.addItem("Use global", "")
        self.promptProviderOverride.addItem("OpenAI", "openai")
        self.promptProviderOverride.addItem("Anthropic", "anthropic")
        self.promptProviderOverride.addItem("Gemini", "gemini")
        self.promptProviderOverride.addItem("OpenRouter", "openrouter")
        self.promptProviderOverride.addItem("Custom", "custom")
        self.promptProviderLayout.addWidget(self.labelPromptProvider)
        self.promptProviderLayout.addWidget(self.promptProviderOverride)
        self.promptProviderLayout.addStretch()
        self.promptDetailsLayout.addLayout(self.promptProviderLayout)

        # Model Override
        self.promptModelLayout = QtWidgets.QHBoxLayout()
        self.labelPromptModel = QtWidgets.QLabel("Model Override:", self.promptDetailsGroup)
        self.promptModelOverride = QtWidgets.QLineEdit(self.promptDetailsGroup)
        self.promptModelLayout.addWidget(self.labelPromptModel)
        self.promptModelLayout.addWidget(self.promptModelOverride)
        self.promptDetailsLayout.addLayout(self.promptModelLayout)

        # System Prompt
        self.labelPromptSystem = QtWidgets.QLabel("System Prompt (optional):", self.promptDetailsGroup)
        self.promptDetailsLayout.addWidget(self.labelPromptSystem)
        self.promptSystemPrompt = QtWidgets.QPlainTextEdit(self.promptDetailsGroup)
        self.promptSystemPrompt.setMaximumHeight(80)
        self.promptDetailsLayout.addWidget(self.promptSystemPrompt)

        # Tuning Overrides
        self.promptTuningLayout = QtWidgets.QHBoxLayout()
        self.labelPromptTemperature = QtWidgets.QLabel("Temperature:", self.promptDetailsGroup)
        self.promptTemperature = QtWidgets.QDoubleSpinBox(self.promptDetailsGroup)
        self.promptTemperature.setRange(-1.0, 2.0)
        self.promptTemperature.setSingleStep(0.1)
        self.promptTemperature.setSpecialValueText("Use global")
        self.promptTemperature.setValue(-1.0)
        self.labelPromptMaxTokens = QtWidgets.QLabel("Max Tokens:", self.promptDetailsGroup)
        self.promptMaxTokens = QtWidgets.QSpinBox(self.promptDetailsGroup)
        self.promptMaxTokens.setRange(-1, 100000)
        self.promptMaxTokens.setSpecialValueText("Use global")
        self.promptMaxTokens.setValue(-1)
        self.promptTuningLayout.addWidget(self.labelPromptTemperature)
        self.promptTuningLayout.addWidget(self.promptTemperature)
        self.promptTuningLayout.addWidget(self.labelPromptMaxTokens)
        self.promptTuningLayout.addWidget(self.promptMaxTokens)
        self.promptTuningLayout.addStretch()
        self.promptDetailsLayout.addLayout(self.promptTuningLayout)

        # Field Mapping (JSON Mode)
        self.labelPromptMapping = QtWidgets.QLabel("JSON Mapping (Key: Field Name):", self.promptDetailsGroup)
        self.promptDetailsLayout.addWidget(self.labelPromptMapping)
        self.promptFieldMapping = QtWidgets.QPlainTextEdit(self.promptDetailsGroup)
        self.promptFieldMapping.setPlaceholderText("translation: Word Translation\nipa: IPA Field")
        self.promptFieldMapping.setMaximumHeight(100)
        self.promptDetailsLayout.addWidget(self.promptFieldMapping)

        # Prompt Text
        self.labelPromptText = QtWidgets.QLabel("Prompt Template:", self.promptDetailsGroup)
        self.promptDetailsLayout.addWidget(self.labelPromptText)
        self.promptText = QtWidgets.QPlainTextEdit(self.promptDetailsGroup)
        self.promptDetailsLayout.addWidget(self.promptText)

        self.tabPromptsLayout.addWidget(self.promptDetailsGroup, 2)

        self.tabWidget.addTab(self.tabPrompts, "")

        # --- Pipelines Tab ---
        self.tabPipelines = QtWidgets.QWidget()
        self.tabPipelines.setObjectName("tabPipelines")
        self.tabPipelinesLayout = QtWidgets.QHBoxLayout(self.tabPipelines)
        
        # Left: List of Pipelines
        self.pipelinesListLayout = QtWidgets.QVBoxLayout()
        self.pipelinesList = QtWidgets.QListWidget(self.tabPipelines)
        self.pipelinesListLayout.addWidget(self.pipelinesList)
        
        self.addPipelineButton = QtWidgets.QPushButton("Add Pipeline", self.tabPipelines)
        self.pipelinesListLayout.addWidget(self.addPipelineButton)
        self.removePipelineButton = QtWidgets.QPushButton("Remove Pipeline", self.tabPipelines)
        self.pipelinesListLayout.addWidget(self.removePipelineButton)
        
        self.tabPipelinesLayout.addLayout(self.pipelinesListLayout, 1) # Stretch factor 1
        
        # Right: Pipeline Details
        self.pipelineDetailsGroup = QtWidgets.QGroupBox("Pipeline Details", self.tabPipelines)
        self.pipelineDetailsGroup.setEnabled(False) # Disabled initially
        self.pipelineDetailsLayout = QtWidgets.QVBoxLayout(self.pipelineDetailsGroup)
        
        self.pipelineNameLayout = QtWidgets.QHBoxLayout()
        self.labelPipelineName = QtWidgets.QLabel("Name:", self.pipelineDetailsGroup)
        self.pipelineName = QtWidgets.QLineEdit(self.pipelineDetailsGroup)
        self.pipelineNameLayout.addWidget(self.labelPipelineName)
        self.pipelineNameLayout.addWidget(self.pipelineName)
        self.pipelineDetailsLayout.addLayout(self.pipelineNameLayout)
        
        self.pipelinePinnedCheckbox = QtWidgets.QCheckBox("Pin to Menu", self.pipelineDetailsGroup)
        self.pipelineDetailsLayout.addWidget(self.pipelinePinnedCheckbox)
        
        self.labelPipelinePrompts = QtWidgets.QLabel("Prompts in Pipeline (Sequential):", self.pipelineDetailsGroup)
        self.pipelineDetailsLayout.addWidget(self.labelPipelinePrompts)
        
        self.pipelinePromptsList = QtWidgets.QListWidget(self.pipelineDetailsGroup)
        self.pipelinePromptsList.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.pipelineDetailsLayout.addWidget(self.pipelinePromptsList)
        
        self.pipelinePromptsControlsLayout = QtWidgets.QHBoxLayout()
        self.addPromptToPipelineButton = QtWidgets.QPushButton("Add Prompt", self.pipelineDetailsGroup)
        self.removePromptFromPipelineButton = QtWidgets.QPushButton("Remove Prompt", self.pipelineDetailsGroup)
        self.pipelinePromptsControlsLayout.addWidget(self.addPromptToPipelineButton)
        self.pipelinePromptsControlsLayout.addWidget(self.removePromptFromPipelineButton)
        self.pipelineDetailsLayout.addLayout(self.pipelinePromptsControlsLayout)
        
        self.tabPipelinesLayout.addWidget(self.pipelineDetailsGroup, 2) # Stretch factor 2

        self.tabWidget.addTab(self.tabPipelines, "")

        # --- Backup Tab ---
        self.tabBackups = QtWidgets.QWidget()
        self.tabBackups.setObjectName("tabBackups")
        self.tabBackupsLayout = QtWidgets.QVBoxLayout(self.tabBackups)
        
        # General Settings Group
        self.backupGeneralGroup = QtWidgets.QGroupBox("General Settings", self.tabBackups)
        self.backupGeneralLayout = QtWidgets.QFormLayout(self.backupGeneralGroup)
        
        self.backupEnabled = QtWidgets.QCheckBox(self.backupGeneralGroup)
        self.backupGeneralLayout.addRow(QtWidgets.QLabel("Enable Backups:", self.backupGeneralGroup), self.backupEnabled)
        
        self.backupInterval = QtWidgets.QSpinBox(self.backupGeneralGroup)
        self.backupInterval.setRange(1, 14400) # 1 min to 10 days
        self.backupInterval.setSuffix(" min")
        self.backupInterval.setToolTip("Recommended: 10 min. Defines how often to check for changes.\nLower values create more granular history (e.g. 10-minute snapshots).")
        self.backupGeneralLayout.addRow(QtWidgets.QLabel("Check Interval:", self.backupGeneralGroup), self.backupInterval)
        
        self.backupOnSettingsOpen = QtWidgets.QCheckBox(self.backupGeneralGroup)
        self.backupGeneralLayout.addRow(QtWidgets.QLabel("Backup on Settings Open:", self.backupGeneralGroup), self.backupOnSettingsOpen)
        
        self.backupPassword = QtWidgets.QLineEdit(self.backupGeneralGroup)
        self.backupPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.backupGeneralLayout.addRow(QtWidgets.QLabel("ZIP Password (Optional):", self.backupGeneralGroup), self.backupPassword)
        
        self.backupNowBtn = QtWidgets.QPushButton(self.backupGeneralGroup)
        self.backupGeneralLayout.addRow(QtWidgets.QLabel("Manual Backup:", self.backupGeneralGroup), self.backupNowBtn)

        self.tabBackupsLayout.addWidget(self.backupGeneralGroup)
        
        # Paths Group
        self.backupPathsGroup = QtWidgets.QGroupBox("Storage Locations", self.tabBackups)
        self.backupPathsLayout = QtWidgets.QGridLayout(self.backupPathsGroup)
        
        self.labelLocalPath = QtWidgets.QLabel("Local Backup Path:", self.backupPathsGroup)
        self.backupLocalPath = QtWidgets.QLineEdit(self.backupPathsGroup)
        self.browseLocalPathBtn = QtWidgets.QPushButton("Browse...", self.backupPathsGroup)
        
        self.backupPathsLayout.addWidget(self.labelLocalPath, 0, 0)
        self.backupPathsLayout.addWidget(self.backupLocalPath, 0, 1)
        self.backupPathsLayout.addWidget(self.browseLocalPathBtn, 0, 2)
        
        self.labelExternalPath = QtWidgets.QLabel("External Path (e.g. Cloud):", self.backupPathsGroup)
        self.backupExternalPath = QtWidgets.QLineEdit(self.backupPathsGroup)
        self.browseExternalPathBtn = QtWidgets.QPushButton("Browse...", self.backupPathsGroup)
        
        self.backupPathsLayout.addWidget(self.labelExternalPath, 1, 0)
        self.backupPathsLayout.addWidget(self.backupExternalPath, 1, 1)
        self.backupPathsLayout.addWidget(self.browseExternalPathBtn, 1, 2)
        
        self.tabBackupsLayout.addWidget(self.backupPathsGroup)
        
        # Rotation Policy Group
        self.backupRotationGroup = QtWidgets.QGroupBox("Retention Policy (GFS Rotation)", self.tabBackups)
        self.backupRotationLayout = QtWidgets.QFormLayout(self.backupRotationGroup)
        
        self.keepTenMin = QtWidgets.QSpinBox(self.backupRotationGroup)
        self.keepTenMin.setRange(0, 1000)
        self.backupRotationLayout.addRow(QtWidgets.QLabel("Keep 10-Min Snapshots (Last Hour):", self.backupRotationGroup), self.keepTenMin)
        
        self.keepHourly = QtWidgets.QSpinBox(self.backupRotationGroup)
        self.keepHourly.setRange(0, 1000)
        self.backupRotationLayout.addRow(QtWidgets.QLabel("Keep Hourly Snapshots (Last Day):", self.backupRotationGroup), self.keepHourly)
        
        self.keepDaily = QtWidgets.QSpinBox(self.backupRotationGroup)
        self.keepDaily.setRange(0, 36500)
        self.backupRotationLayout.addRow(QtWidgets.QLabel("Keep Daily Snapshots:", self.backupRotationGroup), self.keepDaily)
        
        self.keepMonthly = QtWidgets.QSpinBox(self.backupRotationGroup)
        self.keepMonthly.setRange(0, 1200)
        self.backupRotationLayout.addRow(QtWidgets.QLabel("Keep Monthly Snapshots:", self.backupRotationGroup), self.keepMonthly)
        
        self.keepYearly = QtWidgets.QSpinBox(self.backupRotationGroup)
        self.keepYearly.setRange(0, 100)
        self.backupRotationLayout.addRow(QtWidgets.QLabel("Keep Yearly Snapshots:", self.backupRotationGroup), self.keepYearly)

        self.tabBackupsLayout.addWidget(self.backupRotationGroup)
        self.tabBackupsLayout.addStretch()

        self.tabWidget.addTab(self.tabBackups, "")

        # Save Button
        self.saveButton = QtWidgets.QPushButton(SettingsWindow)
        self.saveButton.setObjectName("saveButton")
        self.verticalLayout.addWidget(self.tabWidget)
        self.verticalLayout.addWidget(self.saveButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        self.retranslateUi(SettingsWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(SettingsWindow)

    def retranslateUi(self, SettingsWindow):
        _translate = QtCore.QCoreApplication.translate
        SettingsWindow.setWindowTitle(_translate("SettingsWindow", "IntelliFiller Settings"))
        
        self.labelSelectedApi.setText(_translate("SettingsWindow", "Selected API:"))
        
        self.labelApiKey.setText(_translate("SettingsWindow", "OpenAI API Key:"))
        self.apiKey.setPlaceholderText(_translate("SettingsWindow", "OpenAI API key"))
        self.labelOpenaiModel.setText(_translate("SettingsWindow", "OpenAI Model:"))
        self.openaiModel.setPlaceholderText(_translate("SettingsWindow", "gpt-4o-mini"))
        
        self.labelAnthropicKey.setText(_translate("SettingsWindow", "Anthropic API Key:"))
        self.anthropicKey.setPlaceholderText(_translate("SettingsWindow", "Anthropic API key"))
        self.labelAnthropicModel.setText(_translate("SettingsWindow", "Anthropic Model:"))
        self.anthropicModel.setPlaceholderText(_translate("SettingsWindow", "claude-haiku-4-5"))
        
        self.labelGeminiKey.setText(_translate("SettingsWindow", "Google Gemini API Key:"))
        self.geminiKey.setPlaceholderText(_translate("SettingsWindow", "Google Gemini API key"))
        self.labelGeminiModel.setText(_translate("SettingsWindow", "Google Gemini Model:"))
        self.geminiModel.setPlaceholderText(_translate("SettingsWindow", "gemini-2.0-flash-lite-001"))
        
        self.labelOpenrouterKey.setText(_translate("SettingsWindow", "OpenRouter API Key:"))
        self.openrouterKey.setPlaceholderText(_translate("SettingsWindow", "OpenRouter API Key"))
        self.labelOpenrouterModel.setText(_translate("SettingsWindow", "OpenRouter Model:"))
        self.openrouterModel.setPlaceholderText(_translate("SettingsWindow", "google/gemini-2.0-flash-lite-001"))
        
        self.labelCustomUrl.setText(_translate("SettingsWindow", "OpenAI Compatible Base URL:"))
        self.customUrl.setPlaceholderText(_translate("SettingsWindow", "https://api.example.com/v1"))
        self.labelCustomKey.setText(_translate("SettingsWindow", "OpenAI Compatible API Key:"))
        self.customKey.setPlaceholderText(_translate("SettingsWindow", "API Key"))
        self.labelCustomModel.setText(_translate("SettingsWindow", "OpenAI Compatible Model ID:"))
        self.customModel.setPlaceholderText(_translate("SettingsWindow", "Model ID"))

        self.testConnectionButton.setText(_translate("SettingsWindow", "Test Connection"))

        self.labelEmulate.setText(_translate("SettingsWindow", "Emulate:"))
        self.emulate.setItemText(0, _translate("SettingsWindow", "yes"))
        self.emulate.setItemText(1, _translate("SettingsWindow", "no"))
        self.overwriteFieldLabel.setText(_translate("SettingsWindow", "Overwrite Target Field:"))
        self.overwriteField.setText(_translate("SettingsWindow", ""))
        self.flatMenuLabel.setText(_translate("SettingsWindow", "Show in Root Menu:"))
        self.flatMenu.setText(_translate("SettingsWindow", ""))
        self.flatMenu.setToolTip(_translate("SettingsWindow", "If checked, removes the 'IntelliFiller' submenu and shows items directly in the main context menu."))
        self.labelMaxFavorites.setText(_translate("SettingsWindow", "Max Smart Menu Items:"))
        self.labelObfuscate.setText(_translate("SettingsWindow", "Obfuscate Credentials File:"))
        self.obfuscateCreds.setText(_translate("SettingsWindow", ""))
        self.obfuscateCreds.setToolTip(_translate("SettingsWindow", "Encrypts user_files/credentials.json with a reversible cipher to prevent casual reading."))
        self.labelEncryptionKey.setText(_translate("SettingsWindow", "Custom Encryption Salt:"))
        self.encryptionKey.setPlaceholderText(_translate("SettingsWindow", "Leave empty for default portable key"))
        self.encryptionKey.setToolTip(_translate("SettingsWindow", "Custom string used to encrypt the credentials file. If changed, the file will be re-encrypted."))
        
        self.encryptionKey.setToolTip(_translate("SettingsWindow", "Custom string used to encrypt the credentials file. If changed, the file will be re-encrypted."))
        
        self.labelNetTimeout.setText(_translate("SettingsWindow", "Network Timeout:"))
        self.netTimeout.setToolTip(_translate("SettingsWindow", "Time in seconds to wait for an API response before giving up."))
        
        self.batchGroup.setTitle(_translate("SettingsWindow", "Batch Processing"))
        self.batchEnabled.setText(_translate("SettingsWindow", ""))
        self.batchEnabled.setToolTip(_translate("SettingsWindow", "If enabled, processing will pause periodically to avoid rate limits."))
        self.batchSize.setToolTip(_translate("SettingsWindow", "Number of notes to process before taking a break."))
        self.batchDelay.setToolTip(_translate("SettingsWindow", "Duration of the break in seconds."))
        self.batchRandom.setText(_translate("SettingsWindow", ""))
        self.batchRandom.setToolTip(_translate("SettingsWindow", "Adds a random delay after the batch pause to disperse requests."))
        self.randomDelayMin.setToolTip(_translate("SettingsWindow", "Minimum additional random delay in seconds."))
        self.randomDelayMax.setToolTip(_translate("SettingsWindow", "Maximum additional random delay in seconds."))
        
        self.backupNowBtn.setText(_translate("SettingsWindow", "Backup Now"))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabApi), _translate("SettingsWindow", "API Settings"))
        
        self.addPromptButton.setText(_translate("SettingsWindow", "Add Prompt"))
        self.removePromptButton.setText(_translate("SettingsWindow", "Remove Prompt"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPrompts), _translate("SettingsWindow", "Prompts"))
        
        self.labelPromptName.setText(_translate("SettingsWindow", "Name:"))
        self.promptName.setPlaceholderText(_translate("SettingsWindow", "Prompt Name"))
        self.promptPinnedCheckbox.setText(_translate("SettingsWindow", "Pin to Context Menu"))
        self.labelPromptFormat.setText(_translate("SettingsWindow", "Response Format:"))
        self.labelPromptTarget.setText(_translate("SettingsWindow", "Target Field:"))
        self.promptTargetField.setPlaceholderText(_translate("SettingsWindow", "Target Field"))
        self.labelPromptProvider.setText(_translate("SettingsWindow", "Provider Override:"))
        self.labelPromptModel.setText(_translate("SettingsWindow", "Model Override:"))
        self.promptModelOverride.setPlaceholderText(_translate("SettingsWindow", "Use global model"))
        self.labelPromptSystem.setText(_translate("SettingsWindow", "System Prompt (optional):"))
        self.promptSystemPrompt.setPlaceholderText(_translate("SettingsWindow", "Optional system instructions for this prompt"))
        self.labelPromptTemperature.setText(_translate("SettingsWindow", "Temperature:"))
        self.labelPromptMaxTokens.setText(_translate("SettingsWindow", "Max Tokens:"))
        self.labelPromptMapping.setText(_translate("SettingsWindow", "JSON Mapping (Key: Field Name):"))
        self.labelPromptText.setText(_translate("SettingsWindow", "Prompt Template:"))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPipelines), _translate("SettingsWindow", "Pipelines"))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabBackups), _translate("SettingsWindow", "Backups"))
        
        self.saveButton.setText(_translate("SettingsWindow", "Save"))

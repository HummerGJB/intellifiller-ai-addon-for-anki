import os
import sys
import shutil
import glob
from pathlib import Path
from aqt import mw
from aqt.qt import *
from aqt.qt import *
from aqt.gui_hooks import editor_did_init_buttons, profile_will_close
from aqt.editor import EditorMode, Editor
from aqt.browser import Browser
from aqt.addcards import AddCards
from aqt.addons import AddonManager
from anki.hooks import addHook
from aqt.utils import showWarning

# --- Atomic Rename Strategy Implementation ---

def _gc_cleanup_trash():
    """Cleans up leftover _trash folders from previous updates on startup."""
    addon_dir = Path(__file__).parent
    addons_root = addon_dir.parent
    # Pattern: _intellifiller_trash_* (or _ID_trash_*)
    # We use the actual directory name to be safe, prefixed with _
    trash_pattern = str(addons_root / f"_{addon_dir.name}_trash_*")
    
    for trash_path in glob.glob(trash_pattern):
        try:
            if os.path.isdir(trash_path):
                shutil.rmtree(trash_path)
                print(f"[IntelliFiller] GC cleaned: {trash_path}")
        except OSError:
            pass # Still locked? Ignore until next boot.

# Run GC immediately
_gc_cleanup_trash()

# Monkeypatch Anki's deleteAddon to use atomic rename for this addon
# This prevents PermissionError when updating on Windows
original_deleteAddon = AddonManager.deleteAddon

def patched_deleteAddon(self, dir_name):
    # Check if the deletion target matches our addon
    my_dir_name = os.path.basename(os.path.dirname(__file__))
    
    if dir_name == my_dir_name:
        try:
            from .atomic_installer import atomic_replace
            addon_path = Path(self.addonsFolder()) / dir_name
            # We treat "delete" as moving to trash without replacement
            # atomic_replace handles the "move to trash" part
            if atomic_replace(addon_path, new_content_dir=None):
                print(f"[IntelliFiller] Atomic delete/rename successful for {dir_name}")
                return
        except Exception as e:
            print(f"[IntelliFiller] Atomic delete failed: {e}. Falling back to standard delete.")
    
    # Fallback to original for successful atomic delete (handled internally?) 
    # Or for other addons
    return original_deleteAddon(self, dir_name)

AddonManager.deleteAddon = patched_deleteAddon

# --- End Atomic Rename Implementation ---

# Ensure our addon’s vendor folder is the first thing in sys.path
addon_dir = os.path.dirname(os.path.realpath(__file__))
vendor_path = os.path.join(addon_dir, "vendor")
sys.path.insert(0, vendor_path)

# Platform-specific vendor support (for build_release.py structure)
import platform
system = platform.system().lower()
machine = platform.machine().lower()
sub_vendor = None

if system == 'windows':
    sub_vendor = 'win32'
elif system == 'linux':
    sub_vendor = 'linux'
elif system == 'darwin':
    if 'arm' in machine:
        sub_vendor = 'darwin_arm64'
    else:
        sub_vendor = 'darwin_x86_64'

if sub_vendor:
    sub_vendor_path = os.path.join(vendor_path, sub_vendor)
    if os.path.exists(sub_vendor_path):
        sys.path.insert(0, sub_vendor_path)
        print(f"🔍 Added platform vendor path: {sub_vendor}")

# Debugging information
print("🔍 Anki Addon Loading Dependencies From:", vendor_path)
print("🔍 sys.path includes:", sys.path[:3])


from .settings_editor import SettingsWindow
from .process_notes import process_notes, process_single_note
from .run_prompt_dialog import RunPromptDialog
from .config_manager import ConfigManager
from .backup_manager import BackupManager

ADDON_NAME = 'IntelliFiller'

# Initialize Backup Manager
addon_dir = os.path.dirname(__file__)
backup_service = BackupManager(ConfigManager, addon_dir)




# Check if the correct typing_extensions is loaded
try:
    import typing_extensions
    print("✅ Loaded typing_extensions from:", typing_extensions.__file__)
except ImportError as e:
    print("❌ Failed to load typing_extensions:", e)

# Perform migration if needed
ConfigManager.migrate_legacy_config(__name__)

def handle_edit_current_mode(editor: Editor, prompt_config):
    if not editor or not editor.note:
        showWarning("No active note in editor.")
        return

    editCurrentWindow: EditCurrent = editor.parentWindow
    common_fields = sorted(list(editor.note.keys()))
    dialog = RunPromptDialog(editCurrentWindow, common_fields, prompt_config)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        result = dialog.get_result()
        updated_prompt_config = result["config"]
        if result["save"]:
            save_prompt_config(updated_prompt_config)
        process_single_note(editor, updated_prompt_config)

def handle_add_cards_mode(editor: Editor, prompt_config):
    handle_edit_current_mode(editor, prompt_config)

def save_prompt_config(updated_prompt_config):
    ConfigManager.save_prompt(updated_prompt_config)

def get_common_fields(note_ids):
    if not note_ids:
        return []
    
    # helper to get fields for a note id
    def get_fields(nid):
        try:
            note = mw.col.get_note(nid)
            return set(note.keys())
        except:
            return set()
            
    # Start with fields of first note
    if note_ids:
        common_fields = get_fields(note_ids[0])
    
        # Intersect with rest
        for nid in note_ids[1:]:
            common_fields.intersection_update(get_fields(nid))
            if not common_fields:
                break
                
        return sorted(list(common_fields))
    return []

def create_run_prompt_dialog_from_browser(browser, prompt_config):
    selected_nids = browser.selectedNotes()
    if not selected_nids:
        showWarning("No notes selected.")
        return

    common_fields = get_common_fields(selected_nids)
    
    # We need a parent window. Browser is a QMainWindow.
    dialog = RunPromptDialog(browser, common_fields, prompt_config)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        result = dialog.get_result()
        updated_prompt_config = result["config"]
        if result["save"]:
            save_prompt_config(updated_prompt_config)
            
        process_notes(browser, updated_prompt_config)

def handle_browser_mode(editor, prompt_config):
    browser = None
    if isinstance(editor.parentWindow, Browser):
        browser = editor.parentWindow
    
    if browser:
        create_run_prompt_dialog_from_browser(browser, prompt_config)
    else:
        # Fallback if we cannot find the browser, though EditorMode.BROWSER implies it.
        # Maybe use mw.app.activeWindow() or simply warn.
        # Trying to find ANY open browser:
        for window in mw.app.topLevelWidgets():
            if isinstance(window, Browser):
                browser = window
                break
        
        if browser:
             create_run_prompt_dialog_from_browser(browser, prompt_config)
        else:
             showWarning("Could not determine Browser context.")

def create_run_prompt_dialog_from_editor(editor: Editor, prompt_config):
    if editor.editorMode == EditorMode.BROWSER:
        handle_browser_mode(editor, prompt_config)
    elif editor.editorMode == EditorMode.EDIT_CURRENT:
        handle_edit_current_mode(editor, prompt_config)
    elif editor.editorMode == EditorMode.ADD_CARDS:
        handle_add_cards_mode(editor, prompt_config)

def add_context_menu_items(browser, menu):
    settings = ConfigManager.load_settings()
    flat_menu = settings.get('flatMenu', False) 

    if flat_menu:
        menu.addSeparator() # Add visual separation in root menu
        submenu = menu
    else:
        submenu = QMenu(ADDON_NAME, menu)
        menu.addMenu(submenu)

    prompts = ConfigManager.list_prompts()
    max_favorites = settings.get('maxFavorites', 3)
    history = settings.get('history', [])
    pipelines = settings.get("pipelines", [])

    # Smart Menu Logic
    pinned_items = []
    
    # 1. Pinned Prompts
    for p in prompts:
        if p.get('pinned', False):
            pinned_items.append({"type": "prompt", "config": p, "name": p["promptName"]})
            
            
    # 2. Pinned Pipelines
    for pl in pipelines:
        if pl.get('pinned', False):
             pinned_items.append({"type": "pipeline", "config": pl, "name": pl["pipelineName"]})

    # 3. History (Recent) Items
    # Combine history logic for both prompts and pipelines
    history_items = []
    pinned_names = {item['name'] for item in pinned_items}
    
    for name in history:
        if name in pinned_names:
            continue
            
        # Try to find in prompts
        prompt_match = next((p for p in prompts if p['promptName'] == name), None)
        if prompt_match:
            history_items.append({"type": "prompt", "config": prompt_match, "name": name})
            pinned_names.add(name)
            continue
            
        # Try to find in pipelines
        pipeline_match = next((pl for pl in pipelines if pl['pipelineName'] == name), None)
        if pipeline_match:
             history_items.append({"type": "pipeline", "config": pipeline_match, "name": name})
             pinned_names.add(name)

    # Combine and limit
    smart_items = (pinned_items + history_items)[:max_favorites]

    # Add Smart Items to top level menu
    if smart_items:
        for item in smart_items:
            action = QAction(item["name"], browser)
            
            if item["type"] == "prompt":
                action.triggered.connect(lambda _, br=browser, pc=item["config"]: run_prompt_directly(br, pc))
            elif item["type"] == "pipeline":
                # Resolve pipeline prompts
                resolved_prompts = []
                for prompt_name in item["config"]["prompts"]:
                     match = next((p for p in prompts if p['promptName'] == prompt_name), None)
                     if match:
                         resolved_prompts.append(match)
                if resolved_prompts:
                     action.triggered.connect(lambda _, br=browser, pl=resolved_prompts, name=item["name"]: process_notes(br, pl, name))

            submenu.addAction(action)
        
        submenu.addSeparator()

    # Prompts Submenu
    prompts_menu = QMenu("Prompts", submenu)
    submenu.addMenu(prompts_menu)
    for prompt_config in prompts:
        action = QAction(prompt_config["promptName"], browser)
        action.triggered.connect(lambda _, br=browser, pc=prompt_config: create_run_prompt_dialog_from_browser(br, pc))
        prompts_menu.addAction(action)

    # Pipelines Submenu
    if pipelines:
        pipelines_menu = QMenu("Pipelines", submenu)
        submenu.addMenu(pipelines_menu)
        for pipeline in pipelines:
            action = QAction(pipeline["pipelineName"], browser)
            # Resolve prompts for pipeline
            resolved_prompts = []
            for prompt_name in pipeline["prompts"]:
                match = next((p for p in prompts if p['promptName'] == prompt_name), None)
                if match:
                    resolved_prompts.append(match)
            
            if resolved_prompts:
                action.triggered.connect(lambda _, br=browser, pl=resolved_prompts, name=pipeline["pipelineName"]: process_notes(br, pl, name))
                pipelines_menu.addAction(action)


def run_prompt_directly(browser, prompt_config):
    """Directly run the prompt without showing the dialog."""
    process_notes(browser, prompt_config)


def open_settings():
    # Trigger backup check on settings open if configured
    settings = ConfigManager.load_settings()
    if settings.get('backup', {}).get('backupOnSettingsOpen', True):
        backup_service.perform_backup()
        
    window = SettingsWindow(mw)
    window.exec()


def on_editor_button(editor):
    prompts = ConfigManager.list_prompts()

    menu = QMenu(editor.widget)
    for i, prompt in enumerate(prompts):
        action = QAction(f'Prompt {i + 1}: {prompt["promptName"]}', menu)
        action.triggered.connect(lambda _, p=prompt: create_run_prompt_dialog_from_editor(editor, p))
        menu.addAction(action)

    menu.exec(editor.widget.mapToGlobal(QPoint(0, 0)))


def on_setup_editor_buttons(buttons, editor):
    icon_path = os.path.join(os.path.dirname(__file__), "icon.svg")
    btn = editor.addButton(
        icon=icon_path,
        cmd="run_prompt",
        func=lambda e=editor: on_editor_button(e),
        tip=ADDON_NAME,
        keys=None,
        disables=False
    )
    buttons.append(btn)
    return buttons


addHook("browser.onContextMenu", add_context_menu_items)
mw.addonManager.setConfigAction(__name__, open_settings)
addHook("browser.onContextMenu", add_context_menu_items)
mw.addonManager.setConfigAction(__name__, open_settings)
editor_did_init_buttons.append(on_setup_editor_buttons)

def check_security_cleanup():
    """Silently checks if legacy secrets exist and cleans them up."""
    if ConfigManager.has_legacy_secrets(__name__):
        print(f"[{ADDON_NAME}] Detected legacy secrets. Performing silent cleanup...")
        ConfigManager.sanitize_legacy_files(__name__)

profile_will_close.append(check_security_cleanup)

# Setup Backup Timer
def setup_backup_timer():
    settings = ConfigManager.load_settings()
    backup_config = settings.get('backup', {})
    
    if backup_config.get('enabled', False):
        interval_minutes = backup_config.get('intervalMinutes', 10)
        # Minimum interval 1 minute
        if interval_minutes < 1: interval_minutes = 1
        
        # QTimer takes milliseconds
        interval_ms = interval_minutes * 60 * 1000
        
        timer = QTimer(mw)
        timer.timeout.connect(backup_service.perform_backup)
        timer.start(interval_ms)
        
        # Keep reference to timer to prevent garbage collection
        mw.intellifiller_backup_timer = timer
        
# Initialize timer when profile loads (or strictly now if already loaded, 
# but for Anki addons, we usually hook into profile loaded or just run at init if imported).
# Since this __init__.py runs at Anki startup:
setup_backup_timer()

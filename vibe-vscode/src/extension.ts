/**
 * VL AI Cost Optimizer - VS Code Extension
 * 
 * Main extension entry point. Activates transparent mode to automatically
 * optimize AI coding assistant requests, reducing token costs by 45%.
 */

import * as vscode from 'vscode';
import { TokenSavingsStatusBar } from './ui/statusBar';
import { AnalyticsDashboard } from './ui/dashboard';
import { TransparentModeManager } from './transparent-mode/manager';
import { VLConverter } from './converter/vlConverter';
import { Logger } from './utils/logger';

let statusBar: TokenSavingsStatusBar;
let transparentMode: TransparentModeManager;
let logger: Logger;

export function activate(context: vscode.ExtensionContext) {
    logger = new Logger();
    logger.info('VL AI Cost Optimizer activating...');
    
    // Initialize components
    statusBar = new TokenSavingsStatusBar(context);
    const converter = new VLConverter(context, logger);
    const dashboard = new AnalyticsDashboard(context);
    
    // Check if transparent mode is enabled
    const config = vscode.workspace.getConfiguration('vl');
    const isEnabled = config.get<boolean>('transparentMode.enabled', true);
    
    if (isEnabled) {
        transparentMode = new TransparentModeManager(context, converter, statusBar, logger);
        transparentMode.activate();
        logger.info('Transparent mode activated');
    } else {
        logger.info('Transparent mode disabled in settings');
    }
    
    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('vl.showDashboard', () => {
            dashboard.show();
        }),
        
        vscode.commands.registerCommand('vl.toggleTransparentMode', async () => {
            await toggleTransparentMode(context, converter, statusBar);
        }),
        
        vscode.commands.registerCommand('vl.resetStats', () => {
            statusBar.reset();
            vscode.window.showInformationMessage('VL statistics reset');
        }),
        
        vscode.commands.registerCommand('vl.convertToVL', async () => {
            await convertCurrentFileToVL(converter);
        }),
        
        vscode.commands.registerCommand('vl.compileFromVL', async () => {
            await compileCurrentVLFile(converter);
        })
    );
    
    // Show welcome message on first install
    const hasShownWelcome = context.globalState.get('vl.hasShownWelcome', false);
    if (!hasShownWelcome) {
        showWelcomeMessage(context);
    }
    
    logger.info('VL AI Cost Optimizer activated successfully');
}

export function deactivate() {
    logger?.info('VL AI Cost Optimizer deactivating');
    
    if (transparentMode) {
        transparentMode.deactivate();
    }
}

async function toggleTransparentMode(
    context: vscode.ExtensionContext,
    converter: VLConverter,
    statusBar: TokenSavingsStatusBar
) {
    const config = vscode.workspace.getConfiguration('vl');
    const currentState = config.get<boolean>('transparentMode.enabled', true);
    
    await config.update('transparentMode.enabled', !currentState, vscode.ConfigurationTarget.Global);
    
    if (!currentState) {
        // Enabling
        if (!transparentMode) {
            transparentMode = new TransparentModeManager(context, converter, statusBar, logger);
        }
        transparentMode.activate();
        vscode.window.showInformationMessage('✅ VL Transparent Mode: ON - Saving tokens automatically');
    } else {
        // Disabling
        if (transparentMode) {
            transparentMode.deactivate();
        }
        vscode.window.showInformationMessage('⏸️ VL Transparent Mode: OFF');
    }
}

async function convertCurrentFileToVL(converter: VLConverter) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }
    
    const document = editor.document;
    const language = document.languageId;
    
    if (!['python', 'javascript', 'typescript'].includes(language)) {
        vscode.window.showWarningMessage(`VL conversion not yet supported for ${language}`);
        return;
    }
    
    const code = document.getText();
    
    try {
        const vlCode = await converter.toVL(code, language as 'python' | 'javascript' | 'typescript');
        
        // Create new untitled document with VL code
        const vlDoc = await vscode.workspace.openTextDocument({
            language: 'vl',
            content: vlCode
        });
        
        await vscode.window.showTextDocument(vlDoc);
        
        const originalTokens = estimateTokenCount(code);
        const vlTokens = estimateTokenCount(vlCode);
        const savings = ((originalTokens - vlTokens) / originalTokens * 100).toFixed(1);
        
        vscode.window.showInformationMessage(
            `✅ Converted to VL: ${originalTokens} → ${vlTokens} tokens (${savings}% savings)`
        );
    } catch (error) {
        vscode.window.showErrorMessage(`Conversion failed: ${error}`);
        logger.error('Conversion error', error);
    }
}

async function compileCurrentVLFile(converter: VLConverter) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return;
    }
    
    const document = editor.document;
    if (document.languageId !== 'vl') {
        vscode.window.showWarningMessage('Current file is not a VL file');
        return;
    }
    
    // Ask user for target language
    const target = await vscode.window.showQuickPick(
        ['python', 'javascript', 'typescript'],
        { placeHolder: 'Select target language' }
    );
    
    if (!target) {
        return;
    }
    
    const vlCode = document.getText();
    
    try {
        const targetCode = await converter.fromVL(vlCode, target as 'python' | 'javascript' | 'typescript');
        
        // Create new untitled document with target code
        const targetDoc = await vscode.workspace.openTextDocument({
            language: target,
            content: targetCode
        });
        
        await vscode.window.showTextDocument(targetDoc);
        vscode.window.showInformationMessage(`✅ Compiled VL to ${target}`);
    } catch (error) {
        vscode.window.showErrorMessage(`Compilation failed: ${error}`);
        logger.error('Compilation error', error);
    }
}

function showWelcomeMessage(context: vscode.ExtensionContext) {
    const message = '🎉 VL AI Cost Optimizer installed! Start saving 45% on AI coding costs automatically.';
    const actions = ['Show Dashboard', 'Learn More', 'Settings'];
    
    vscode.window.showInformationMessage(message, ...actions).then(selection => {
        if (selection === 'Show Dashboard') {
            vscode.commands.executeCommand('vl.showDashboard');
        } else if (selection === 'Learn More') {
            vscode.env.openExternal(vscode.Uri.parse('https://github.com/pmarmaroli/vibe-language'));
        } else if (selection === 'Settings') {
            vscode.commands.executeCommand('workbench.action.openSettings', 'vl');
        }
    });
    
    context.globalState.update('vl.hasShownWelcome', true);
}

function estimateTokenCount(text: string): number {
    // Rough estimation: ~4 chars per token on average
    // This is simplified - real implementation would use tiktoken or similar
    return Math.ceil(text.length / 4);
}

/**
 * Analytics Dashboard - Webview showing detailed cost savings
 */

import * as vscode from 'vscode';

export class AnalyticsDashboard {
    private panel: vscode.WebviewPanel | undefined;
    
    constructor(private context: vscode.ExtensionContext) {}
    
    show() {
        if (this.panel) {
            this.panel.reveal(vscode.ViewColumn.One);
            return;
        }
        
        this.panel = vscode.window.createWebviewPanel(
            'vlDashboard',
            '💰 VL Cost Savings Dashboard',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );
        
        this.panel.webview.html = this.getHtmlContent();
        
        this.panel.onDidDispose(() => {
            this.panel = undefined;
        }, null, this.context.subscriptions);
        
        // Handle messages from webview
        this.panel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'resetStats':
                        vscode.commands.executeCommand('vl.resetStats');
                        break;
                    case 'openSettings':
                        vscode.commands.executeCommand('workbench.action.openSettings', 'vl');
                        break;
                }
            },
            undefined,
            this.context.subscriptions
        );
    }
    
    private getHtmlContent(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VL Cost Savings Dashboard</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 20px;
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
        }
        
        h1 {
            color: var(--vscode-textLink-foreground);
            border-bottom: 1px solid var(--vscode-panel-border);
            padding-bottom: 10px;
        }
        
        .hero {
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, var(--vscode-button-background), var(--vscode-button-hoverBackground));
            border-radius: 8px;
            margin-bottom: 30px;
        }
        
        .hero h2 {
            font-size: 48px;
            margin: 0;
            color: var(--vscode-button-foreground);
        }
        
        .hero p {
            font-size: 18px;
            margin: 10px 0 0 0;
            color: var(--vscode-button-foreground);
            opacity: 0.9;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: var(--vscode-editor-inactiveSelectionBackground);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            padding: 20px;
        }
        
        .stat-card h3 {
            margin: 0 0 10px 0;
            font-size: 14px;
            color: var(--vscode-descriptionForeground);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-card .value {
            font-size: 36px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
            margin-bottom: 5px;
        }
        
        .stat-card .label {
            font-size: 14px;
            color: var(--vscode-descriptionForeground);
        }
        
        .info-section {
            background: var(--vscode-textBlockQuote-background);
            border-left: 4px solid var(--vscode-textLink-foreground);
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        
        .info-section h3 {
            margin: 0 0 10px 0;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        button {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        
        button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        
        button.secondary {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        
        button.secondary:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }
        
        .coming-soon {
            text-align: center;
            padding: 40px;
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 8px;
            margin-top: 30px;
        }
        
        .coming-soon h2 {
            color: var(--vscode-textLink-foreground);
            margin-bottom: 15px;
        }
        
        .feature-list {
            list-style: none;
            padding: 0;
        }
        
        .feature-list li {
            padding: 8px 0;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        
        .feature-list li:last-child {
            border-bottom: none;
        }
        
        .feature-list li::before {
            content: "🚀 ";
        }
    </style>
</head>
<body>
    <h1>💰 VL Cost Savings Dashboard</h1>
    
    <div class="hero">
        <h2>Coming Soon!</h2>
        <p>Transparent mode is in active development</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <h3>Token Reduction</h3>
            <div class="value">45.1%</div>
            <div class="label">Average savings (proven)</div>
        </div>
        
        <div class="stat-card">
            <h3>Best Case</h3>
            <div class="value">84.8%</div>
            <div class="label">Data pipeline scenarios</div>
        </div>
        
        <div class="stat-card">
            <h3>Status</h3>
            <div class="value">Alpha</div>
            <div class="label">Extension version 0.2.0</div>
        </div>
    </div>
    
    <div class="info-section">
        <h3>📌 Current Status</h3>
        <p>The VL compiler is production-ready for Python conversion. The transparent mode extension is under active development.</p>
        <p><strong>What works now:</strong></p>
        <ul>
            <li>✅ Python ↔ VL bidirectional conversion (100% success rate)</li>
            <li>✅ VL → Python/JavaScript/TypeScript compilation</li>
            <li>✅ Token efficiency benchmarks (45.1% average)</li>
            <li>✅ Manual conversion commands</li>
        </ul>
    </div>
    
    <div class="coming-soon">
        <h2>🔜 Transparent Mode Features (Q2 2026)</h2>
        <ul class="feature-list">
            <li>Automatic Copilot request optimization</li>
            <li>Real-time token savings tracking</li>
            <li>Interactive cost calculator</li>
            <li>Weekly savings reports</li>
            <li>Team analytics (Enterprise)</li>
            <li>Cursor IDE integration</li>
        </ul>
    </div>
    
    <div class="button-group">
        <button onclick="tryManualConversion()">Try Manual Conversion</button>
        <button class="secondary" onclick="openSettings()">Settings</button>
        <button class="secondary" onclick="learnMore()">Learn More</button>
    </div>
    
    <script>
        const vscode = acquireVsCodeApi();
        
        function tryManualConversion() {
            alert('Open a Python file and use:\\n\\nCommand Palette → "VL: Convert Current File to VL"\\n\\nThis will show you the token-optimized VL version!');
        }
        
        function openSettings() {
            vscode.postMessage({ command: 'openSettings' });
        }
        
        function learnMore() {
            // This would open external link in real implementation
            alert('Visit: https://github.com/pmarmaroli/vibe-language');
        }
    </script>
</body>
</html>`;
    }
}

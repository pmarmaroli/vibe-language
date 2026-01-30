/**
 * VL Converter - Bridge to Python-based VL compiler
 * Handles bidirectional conversion: Python/JS/TS ↔ VL
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { spawn } from 'child_process';
import { Logger } from '../utils/logger';

export class VLConverter {
    private pythonPath: string;
    private converterScript: string;
    private vlRoot: string;
    
    constructor(
        private context: vscode.ExtensionContext,
        private logger: Logger
    ) {
        const config = vscode.workspace.getConfiguration('vl');
        this.pythonPath = config.get<string>('compiler.pythonPath', 'python');
        
        // Find VL root directory (assume extension is in vibe-language/vibe-vscode)
        this.vlRoot = path.resolve(context.extensionPath, '..');
        this.converterScript = path.join(this.vlRoot, 'src', 'vl', 'py2vl.py');
        
        this.logger.debug('VLConverter initialized', {
            pythonPath: this.pythonPath,
            vlRoot: this.vlRoot,
            converterScript: this.converterScript
        });
    }
    
    /**
     * Convert source code to VL
     */
    async toVL(code: string, language: 'python' | 'javascript' | 'typescript'): Promise<string> {
        this.logger.debug(`Converting ${language} to VL (${code.length} chars)`);
        
        if (language === 'python') {
            return this.pythonToVL(code);
        } else {
            // JavaScript/TypeScript conversion not yet implemented
            throw new Error(`${language} → VL conversion not yet implemented. Python conversion available now.`);
        }
    }
    
    /**
     * Convert VL code to target language
     */
    async fromVL(vlCode: string, targetLanguage: 'python' | 'javascript' | 'typescript'): Promise<string> {
        this.logger.debug(`Converting VL to ${targetLanguage} (${vlCode.length} chars)`);
        
        const args = [
            '-m', 'vl.cli',
            '--target', targetLanguage === 'typescript' ? 'typescript' : 
                       targetLanguage === 'javascript' ? 'javascript' : 'python',
            '-'  // Read from stdin
        ];
        
        try {
            const result = await this.runPython(args, vlCode);
            this.logger.debug(`Conversion complete: ${result.length} chars`);
            return result;
        } catch (error) {
            this.logger.error('VL compilation failed', error);
            throw error;
        }
    }
    
    /**
     * Convert Python code to VL using py2vl module
     */
    private async pythonToVL(pythonCode: string): Promise<string> {
        const args = [
            '-m', 'vl.py2vl',
            '-'  // Read from stdin
        ];
        
        try {
            const result = await this.runPython(args, pythonCode);
            this.logger.debug(`Python → VL conversion complete: ${result.length} chars`);
            return result;
        } catch (error) {
            this.logger.error('Python → VL conversion failed', error);
            throw error;
        }
    }
    
    /**
     * Run Python script with stdin/stdout
     */
    private runPython(args: string[], stdin?: string): Promise<string> {
        return new Promise((resolve, reject) => {
            // Set PYTHONPATH to include VL source
            const env = { 
                ...process.env,
                PYTHONPATH: path.join(this.vlRoot, 'src')
            };
            
            this.logger.debug('Running Python', { 
                command: this.pythonPath, 
                args,
                env: { PYTHONPATH: env.PYTHONPATH }
            });
            
            const proc = spawn(this.pythonPath, args, {
                cwd: this.vlRoot,
                env
            });
            
            let stdout = '';
            let stderr = '';
            
            proc.stdout.on('data', (data) => {
                stdout += data.toString();
            });
            
            proc.stderr.on('data', (data) => {
                stderr += data.toString();
            });
            
            proc.on('error', (error) => {
                this.logger.error('Python process error', error);
                reject(new Error(`Failed to start Python: ${error.message}`));
            });
            
            proc.on('close', (code) => {
                if (code === 0) {
                    resolve(stdout);
                } else {
                    this.logger.error('Python process failed', { code, stderr });
                    reject(new Error(`Python exited with code ${code}: ${stderr}`));
                }
            });
            
            // Send stdin if provided
            if (stdin) {
                proc.stdin.write(stdin);
                proc.stdin.end();
            }
        });
    }
    
    /**
     * Test if Python and VL modules are available
     */
    async test(): Promise<{ success: boolean; error?: string }> {
        try {
            this.logger.debug('Testing VL converter');
            
            const testCode = 'def test(): return 42';
            const vlCode = await this.pythonToVL(testCode);
            
            if (vlCode.includes('fn:test')) {
                this.logger.info('VL converter test passed');
                return { success: true };
            } else {
                return { success: false, error: 'Unexpected VL output' };
            }
        } catch (error: any) {
            this.logger.error('VL converter test failed', error);
            return { success: false, error: error.message };
        }
    }
}

import { Component } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';

@Component({
  selector: 'app-chat-bot',
  standalone: true,
  imports: [CommonModule, DatePipe],
  templateUrl: './chat-bot.html',
  styleUrls: ['./chat-bot.css']
})
export class ChatBot {
  isOpen = false;

  toggleChat(): void {
    this.isOpen ? this.closeChat() : this.openChat();
  }

  openChat(): void {
    this.isOpen = true;
  }

  closeChat(): void {
    this.isOpen = false;
  }

  messages: Array<{ role: 'user' | 'bot'; text: string; time: Date }> = [];

  draft = '';

  sendMessage(): void {
    const text = this.draft?.trim();
    if (!text) return;

    this.messages.push({ role: 'user', text, time: new Date() });

    this.draft = '';

  }

  addBotMessage(text: string): void {
    this.messages.push({ role: 'bot', text, time: new Date() });
  }

  handleKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  loadHistory(): void {
  }

  saveHistory(): void {
  }

  clearConversation(): void {
    this.messages = [];
  }

  saveDraft(): void {
  }

  loadDraft(): void {
  }

  protected readonly HTMLTextAreaElement = HTMLTextAreaElement;
}

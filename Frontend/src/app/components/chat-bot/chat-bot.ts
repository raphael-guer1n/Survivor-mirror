import { Component, Injectable, inject } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {BackendInterface} from "../../cores/interfaces/backend/backend-interface";
import {AuthService} from '../../cores/services/auth-service/auth';
import {User} from '../../cores/interfaces/backend/dtos';

@Component({
  selector: 'app-chat-bot',
  standalone: true,
  imports: [CommonModule, DatePipe, FormsModule],
  templateUrl: './chat-bot.html',
  styleUrls: ['./chat-bot.css']
})
export class ChatBot {
  isOpen = false;
  logged = false;
  reciver_name = "";
  sender = "";
  private backend = inject(BackendInterface);
  private auth = inject(AuthService);
  
  toggleChat_access(): void {
    console.log(this.auth.user)
    console.log(this.reciver_name)
    if (this.auth.isAuthenticated && this.auth.user) {
      this.logged = true;
      this.sender = this.auth.user.email;
      console.log(this.logged);
      console.log(this.sender);
    }
    else {
      this.logged = false;
      console.log(this.logged);
    } 
  }

  toggleChat(): void {
    this.isOpen ? this.closeChat() : this.openChat();
  }

  openChat(): void {
    this.isOpen = true;
  }

  closeChat(): void {
    this.isOpen = false;
  }

  messages: Array<{ role: 'sender' | 'reciver'; text: string; time: Date }> = [];

  draft = '';

  sendMessage(): void {
    const text = this.draft?.trim();
    if (!text) return;

    this.messages.push({ role: 'sender', text, time: new Date() });

    this.draft = '';

  }

  read_message(text: string): void {
    this.messages.push({ role: 'reciver', text, time: new Date() });
  }

  handleKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  load_conversation(): void {
    this.backend.getConversation(this.sender, this.reciver_name);
  }

  clearConversation(): void {
    this.messages = [];
  }

  get_reciver_name(text: string): void {
    this.reciver_name = text;
    console.log(this.reciver_name)
  }

  protected readonly HTMLTextAreaElement = HTMLTextAreaElement;
}

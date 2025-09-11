import { Component, Injectable, inject } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {BackendInterface} from "../../cores/interfaces/backend/backend-interface";
import {AuthService} from '../../cores/services/auth-service/auth';
import {interval, Subscription} from 'rxjs';
import {Communication} from '../../cores/interfaces/backend/dtos';

@Component({
  selector: 'app-chat-bot',
  standalone: true,
  imports: [CommonModule, DatePipe, FormsModule],
  templateUrl: './chat-bot.html',
  styleUrls: ['./chat-bot.css']
})


export class ChatBot {
  isOpen: boolean = false;
  logged: boolean = false;
  id_of_user: number = -1
  email: string[] = []
  last_message: string[] = []
  reciver_name = "";
  sender: string = "";
  id_of_logged = "";
  ids: any[] = []
  conversation: Communication[] = []
  display_conversation: any = -1
  private reloadSub!: Subscription;
  private backend = inject(BackendInterface);
  private auth = inject(AuthService);
  
  get_last_message_and_email(id: number, id_user: number) {
    this.backend.get_last_message_by_id(id, id_user).subscribe({
      next: (msg) => {
          this.email[this.email.length] = msg.sender_name
          this.last_message[this.last_message.length] = msg.content
          console.log("dans init pour emails", this.email, id, id_user);
    },})
  }


  ngOnInit(): void {
    this.reloadSub = interval(2000).subscribe(() => {
      if (this.isOpen && this.display_conversation === -1 && this.auth.isAuthenticated && this.auth.user) {
        this.backend.get_Conversations_of_user(this.id_of_user).subscribe({
          next: (msg) => {
              this.ids = msg;
              this.email = [];
              this.last_message = []
              console.log("dans init", this.ids);
              for (let tmp of this.ids) {
                console.log(tmp);
                this.get_last_message_and_email(tmp, this.id_of_user);
              }
        },})
      }
      if (this.display_conversation !== -1) {
        this.backend.get_Conversations_content(this.ids[this.display_conversation]).subscribe({
          next: (msg) => {
            this.conversation = msg;
          },})
      }
    });
  }

  toggleChat_access(): void {
    if (this.auth.isAuthenticated && this.auth.user) {
      this.logged = true;
      this.sender = this.auth.user.email;
      this.id_of_user = this.auth.user.id;
      this.backend.get_Conversations_of_user(this.auth.user.id).subscribe({
        next: (msg) => {
            this.ids = msg;
            console.log("de chat access", this.ids);
            for (let tmp of this.ids) {
              this.get_last_message_and_email(tmp, this.id_of_user);
            }
      },})

    }
    else {
      this.logged = false;
      this.email = []
      this.last_message = []
      this.reciver_name = "";
      this.sender = "";
      this.id_of_logged = "";
      this.ids = []
      this.conversation = []
      this.display_conversation = -1
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
    this.logged = false;
    this.email = []
    this.last_message = []
    this.reciver_name = "";
    this.sender = "";
    this.id_of_logged = "";
    this.ids = []
    this.conversation = []
    this.display_conversation = -1
  }

  messages: Array<{ role: 'sender' | 'reciver'; text: string; time: Date }> = [];

  draft = '';

  openConversation(id: number, id_list: number) {
      console.log(this.display_conversation, "id", id, "id list", id_list, "value", this.ids[id_list]);
      console.log(this.ids);
      console.log(this.email, this.email[id_list]);
      this.backend.get_Conversations_content(this.ids[id_list]).subscribe({
        next: (msg) => {
          this.conversation = msg;
          },})
          this.display_conversation = id_list;
  }

  sendMessage(): void {
    const text = this.draft?.trim();
    if (!text) return;

    this.backend.send_message(this.sender, this.email[this.display_conversation], text, this.ids[this.display_conversation])
    .subscribe({
        next: () =>{
        this.draft = '';
        this.conversation = []
        this.backend.get_Conversations_content(this.ids[this.display_conversation]).subscribe({
          next: (msg) => {
            this.conversation = msg;
          },})
      },})
  }

  create_a_new_conversation() {
    const text = this.draft?.trim();
    if (!text) return;

    console.log(this.id_of_user, " /", this.draft?.trim(), "/ a");
    this.backend.create_conversation(this.id_of_user, this.draft?.trim())
    this.draft = '';
    console.log("we done");
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
    console.log("c'est qu jean?", this.ids);
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

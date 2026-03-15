export interface MessagePart {
    type: "text" | "tool_call" | "tool_return";
    content?: string;
    tool_name?: string;
    args?: Record<string, any>;
}

export interface Message {
    role: "user" | "model";
    parts: MessagePart[];
}

export interface ChatRequest {
    message: string;
    session_id?: string;
}

export interface ChatResponse {
    response: string;
    session_id: string;
    history: Message[];
}

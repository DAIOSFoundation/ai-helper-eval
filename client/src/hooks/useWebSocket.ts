import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';

interface WebSocketHook {
    socket: Socket | null;
    isConnected: boolean;
    sendPing: (message?: string) => void;
    lastPong: string | null;
}

export const useWebSocket = (url: string = 'http://localhost:5001'): WebSocketHook => {
    const [socket, setSocket] = useState<Socket | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const [lastPong, setLastPong] = useState<string | null>(null);
    const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        // Socket.IO 연결
        const newSocket = io(url, {
            transports: ['websocket', 'polling'],
            timeout: 20000,
            forceNew: true
        });

        newSocket.on('connect', () => {
            console.log('웹소켓 연결됨');
            setIsConnected(true);

            // 30초마다 핑 전송
            pingIntervalRef.current = setInterval(() => {
                newSocket.emit('ping', `ping-${Date.now()}`);
            }, 30000);
        });

        newSocket.on('disconnect', () => {
            console.log('웹소켓 연결 해제됨');
            setIsConnected(false);

            if (pingIntervalRef.current) {
                clearInterval(pingIntervalRef.current);
                pingIntervalRef.current = null;
            }
        });

        newSocket.on('pong', (data: { message: string; timestamp: string }) => {
            console.log('퐁 수신:', data.message);
            setLastPong(data.timestamp);
        });

        newSocket.on('connected', (data: any) => {
            console.log('서버 연결 확인:', data);
        });

        setSocket(newSocket);

        return () => {
            if (pingIntervalRef.current) {
                clearInterval(pingIntervalRef.current);
            }
            newSocket.close();
        };
    }, [url]);

    const sendPing = (message: string = `ping-${Date.now()}`) => {
        if (socket && isConnected) {
            socket.emit('ping', message);
            console.log('핑 전송:', message);
        }
    };

    return {
        socket,
        isConnected,
        sendPing,
        lastPong
    };
};

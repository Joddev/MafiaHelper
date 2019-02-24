const ws = {};

ws.socket = (url, handler) => {
    const socket = new WebSocket(`ws://${url}`);

    socket.send_json = (json) => socket.send(JSON.stringify(json));

    socket.onclose = () => {
        console.error('Socket closed unexpectedly!');
        alert('Socket closed unexpectedly!');
    };

    socket.onmessage = (e) => {
        handler.accept(JSON.parse(e.data));
    };

    return socket;
};

export default ws;

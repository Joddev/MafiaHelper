import ws from '../socket';
import handler, { app } from '../handler';

app.socket = ws.socket(window.location.host + '/ws/', handler);


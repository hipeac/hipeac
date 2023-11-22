import { marked } from 'marked';

const render = (text: string) => {
  return marked.parse(text);
};

export { render };

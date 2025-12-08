export function el(tag, attrs = {}, ...children){
  const e = document.createElement(tag);
  Object.entries(attrs).forEach(([k,v]) => e.setAttribute(k,v));
  children.flat().forEach(c => e.append(typeof c === 'string' ? document.createTextNode(c) : c));
  return e;
}

export function formatDateISO(date = new Date()){
  return new Date(date).toLocaleString();
}

// Lightweight text contrast regression check for this solid-surface design.
// Raster product screenshots, decorative overlay gradients and focus outlines are outside scope.
() => {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 1;
  const context = canvas.getContext('2d', { willReadFrequently: true });
  function rgba(color) {
    context.clearRect(0, 0, 1, 1);
    context.fillStyle = color;
    context.fillRect(0, 0, 1, 1);
    return [...context.getImageData(0, 0, 1, 1).data].map((value, index) => index === 3 ? value / 255 : value);
  }
  function blend(foreground, background) {
    return foreground.slice(0, 3).map((value, index) => value * foreground[3] + background[index] * (1 - foreground[3]));
  }
  function luminance(color) {
    return color.map(value => {
      value /= 255;
      return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
    }).reduce((sum, value, index) => sum + value * [0.2126, 0.7152, 0.0722][index], 0);
  }
  function contrast(foreground, background) {
    const a = luminance(foreground);
    const b = luminance(background);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
  }
  return [...document.querySelectorAll('body *')]
    .filter(element => {
      if (!element.checkVisibility()) return false;
      // Gradient headline text paints through background-clip, so its colour is intentionally
      // transparent; contrast for that text comes from the gradient background layer.
      const style = getComputedStyle(element);
      if ((style.webkitBackgroundClip || style.backgroundClip) === 'text') return false;
      return [...element.childNodes].some(node => node.nodeType === 3 && node.textContent.trim());
    })
    .flatMap(element => {
      const style = getComputedStyle(element);
      const ancestors = [];
      for (let node = element; node; node = node.parentElement) ancestors.unshift(node);
      let background = [255, 255, 255];
      for (const node of ancestors) background = blend(rgba(getComputedStyle(node).backgroundColor), background);
      const foreground = blend(rgba(style.color), background);
      // Text sitting on a linear gradient is checked against every colour stop: worst case wins.
      const image = style.backgroundImage;
      const stops = image && image.includes('linear-gradient')
        ? (image.match(/(?:rgba?|hsl|oklch|oklab|lab|lch|color)\([^)]*\)/g) || []).map(rgba)
        : [];
      const surfaces = stops.length ? stops.map(stop => blend(stop, background)) : [background];
      const ratio = Math.min(...surfaces.map(surface => contrast(foreground, surface)));
      const size = parseFloat(style.fontSize);
      const minimum = size >= 24 || (size >= 18.66 && parseInt(style.fontWeight) >= 700) ? 3 : 4.5;
      return ratio + 0.03 < minimum ? [{ text: element.textContent.trim().slice(0, 80), ratio: ratio.toFixed(2) }] : [];
    });
}

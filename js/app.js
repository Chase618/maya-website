/* ========== App.js - Maya Website ========== */

// Utility: get image URL relative to site root
// Detects the repo base path from the current script URL
let _basePath = '';
function getBasePath() {
  if (_basePath) return _basePath;
  const scripts = document.getElementsByTagName('script');
  for (const s of scripts) {
    if (s.src && s.src.includes('/js/app.js')) {
      // e.g. /maya-website/js/app.js -> /maya-website
      _basePath = s.src.replace(/\/js\/app\.js.*$/, '');
      return _basePath;
    }
  }
  return '';
}

function img(path) {
  if (!path) return '';
  // Ensure path is relative to site root
  if (path.startsWith('images/')) {
    return getBasePath() + '/' + path;
  }
  return path;
}

// Utility: slug from name (keeps Chinese chars for uniqueness, modern browsers handle UTF-8 URLs)
function slug(name) {
  return name
    .toLowerCase()
    .replace(/[^\w一-鿿]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

// Utility: extract clean display name
function displayName(name) {
  return name
    .replace(/\(.*\)/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

// ========== Product data loaded from JSON ==========
let productsData = null;

async function loadProducts() {
  if (productsData) return productsData;
  const res = await fetch(getBasePath() + '/products.json');
  productsData = await res.json();
  return productsData;
}

// ========== Get all products flat ==========
function getAllProducts(data) {
  const all = [];

  // Monitors
  if (data.monitors) {
    for (const [sub, prods] of Object.entries(data.monitors)) {
      for (const p of prods) {
        all.push({ ...p, category: 'monitors', subCategory: sub });
      }
    }
  }

  // AIOs
  if (data.aios) {
    for (const p of data.aios || []) {
      all.push({ ...p, category: 'aios', subCategory: '' });
    }
  }

  // Others
  if (data.others) {
    for (const [sub, prods] of Object.entries(data.others)) {
      for (const p of prods) {
        all.push({ ...p, category: 'others', subCategory: sub });
      }
    }
  }

  return all;
}

// ========== Product page URL builder ==========
function productUrl(p) {
  // Use pre-computed page_url from products.json
  let url = p.page_url;
  if (url) return getBasePath() + '/' + url;
  // Fallback: generate from name
  const cat = p.category || '';
  const sub = p.subCategory || '';
  const name = slug(p.display_name || p.name);
  return getBasePath() + '/' + (cat + (sub ? '/' + sub : '') + '/' + name + '.html');
}

// ========== Render product cards in a grid ==========
function renderProductGrid(container, products) {
  if (!container || !products.length) {
    console.warn('renderProductGrid: no products or no container', { container, count: products?.length });
    return;
  }

  container.innerHTML = products.map(p => {
    const thumb = img(p.thumb || p.images[0]);
    const url = productUrl(p);
    const tag = getCategoryLabel(p.category, p.subCategory);
    // Uppercase any English letters in display name
    let displayName = p.display_name || p.name;
    displayName = displayName.replace(/[a-z]/g, c => c.toUpperCase());
    return `
      <div class="product-card" onclick="location.href='${url}'">
        <div class="product-card-image">
          <img src="${thumb}" alt="${displayName}" loading="lazy">
        </div>
        <div class="product-card-body">
          <div class="product-card-name">${displayName}</div>
          ${tag ? `<span class="product-card-tag">${tag}</span>` : ''}
        </div>
      </div>
    `;
  }).join('');
}

// ========== Category label mapping ==========
function getCategoryLabel(cat, sub) {
  const labels = {
    monitors: {
      '商用系列': '商用系列',
      '电竞系列': '电竞系列',
      '设计系列': '设计系列',
      '专业系列': '专业系列'
    },
    aios: { '': '一体机' },
    others: {
      'VR类目': 'VR设备',
      '插座类目': '插座/转换器',
      '笔记本电脑类目': '笔记本电脑'
    }
  };
  return (labels[cat] && labels[cat][sub]) || '';
}

// ========== Hero image selector ==========
function getHeroImage(cat) {
  const map = {
    monitors: 'images/monitors/commercial/air-24-air24/1.jpg',
    aios: 'images/aios/maya-white-whale-gs24/maya-gs24-1.jpg',
    others: 'images/others/vr/maya-vr-headset/1.jpg'
  };
  return map[cat] || '';
}

// ========== Fade-in observer ==========
function observeFadeIns() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.fade-in:not(.visible)').forEach(el => observer.observe(el));
}

// ========== Mobile nav toggle ==========
function initMobileNav() {
  const toggle = document.querySelector('.nav-mobile-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      links.classList.toggle('active');
    });
  }
}

// ========== Lightbox ==========
function openLightbox(src) {
  let lb = document.querySelector('.lightbox');
  if (!lb) {
    lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.innerHTML = '<button class="lightbox-close">&times;</button><img src="" alt="">';
    lb.addEventListener('click', () => lb.classList.remove('active'));
    document.body.appendChild(lb);
  }
  lb.querySelector('img').src = src;
  lb.classList.add('active');
}

// ========== Product gallery ==========
function initProductGallery() {
  const thumbs = document.querySelectorAll('.product-thumb');
  const mainImg = document.querySelector('.product-gallery-main img');
  if (!thumbs.length || !mainImg) return;

  thumbs.forEach(thumb => {
    thumb.addEventListener('click', () => {
      thumbs.forEach(t => t.classList.remove('active'));
      thumb.classList.add('active');
      const src = thumb.querySelector('img').src;
      mainImg.src = src;
    });
  });
}

// ========== Detail page image click ==========
function initDetailImages() {
  document.querySelectorAll('.product-detail-images img').forEach(img => {
    img.style.cursor = 'pointer';
    img.addEventListener('click', () => openLightbox(img.src));
  });
}

// ========== Init ==========
document.addEventListener('DOMContentLoaded', () => {
  initMobileNav();
  observeFadeIns();
  initProductGallery();
  initDetailImages();
});

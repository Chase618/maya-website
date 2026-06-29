/* ========== App.js - Maya Website ========== */

// Utility: get image URL relative to project root
function img(path) {
  if (!path) return '';
  return path.replace(/^images\//, '');
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
  const res = await fetch('products.json');
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
  const cat = p.category || '';
  const sub = p.subCategory || '';
  const name = slug(p.name);
  return `${cat}/${sub ? sub + '/' : ''}${name}.html`;
}

// ========== Render product cards in a grid ==========
function renderProductGrid(container, products) {
  if (!container || !products.length) return;

  container.innerHTML = products.map(p => {
    const thumb = img(p.thumb || p.images[0]);
    const url = productUrl(p);
    const tag = getCategoryLabel(p.category, p.subCategory);
    return `
      <div class="product-card fade-in" onclick="location.href='${url}'">
        <div class="product-card-image">
          <img src="${thumb}" alt="${p.name}" loading="lazy">
        </div>
        <div class="product-card-body">
          <div class="product-card-name">${p.name}</div>
          ${tag ? `<span class="product-card-tag">${tag}</span>` : ''}
        </div>
      </div>
    `;
  }).join('');

  // Trigger fade-in
  setTimeout(() => observeFadeIns(), 100);
}

// ========== Category label mapping ==========
function getCategoryLabel(cat, sub) {
  const labels = {
    monitors: {
      commercial: '商用系列',
      gaming: '电竞系列',
      design: '设计系列',
      professional: '专业系列'
    },
    aios: { '': '一体机' },
    others: {
      'VR类目': 'VR产品',
      '插座类目': '插座/转换器',
      '笔记本电脑类目': '笔记本电脑'
    }
  };
  return (labels[cat] && labels[cat][sub]) || '';
}

// ========== Hero image selector ==========
function getHeroImage(cat) {
  // Pick a good hero image from the category
  const map = {
    monitors: 'images/monitors/commercial/Air 24(Air系列24英寸显示器)/AIR 24-1白底图.jpg',
    aios: 'images/aios/MAYA 白鲸 GS24/MAYA 白鲸 GS24-1.jpg',
    others: 'images/others/VR类目/玛雅VR头盔/VR主图-1.jpg'
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

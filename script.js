const menuToggle = document.querySelector("[data-menu-toggle]");
const mobileMenu = document.querySelector("[data-mobile-menu]");
const filterButtons = document.querySelectorAll("[data-filter]");
const caseCards = document.querySelectorAll(".portfolio .case-card");
const previewCards = document.querySelectorAll(".case-card, .ai-showcase");
const leadForm = document.querySelector("[data-lead-form]");
const formNote = document.querySelector("[data-form-note]");

menuToggle?.addEventListener("click", () => {
  const isOpen = mobileMenu.classList.toggle("open");
  menuToggle.setAttribute("aria-expanded", String(isOpen));
});

mobileMenu?.addEventListener("click", (event) => {
  if (event.target.matches("a")) {
    mobileMenu.classList.remove("open");
    menuToggle?.setAttribute("aria-expanded", "false");
  }
});

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const filter = button.dataset.filter;

    filterButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");

    caseCards.forEach((card) => {
      const shouldShow = filter === "all" || card.dataset.category === filter;
      card.classList.toggle("hidden", !shouldShow);
      const video = card.querySelector("video");
      if (video && !shouldShow) {
        video.pause();
        video.currentTime = 0;
        card.classList.remove("is-playing");
      }
    });
  });
});

const ensureVideoSources = (video) => {
  if (video.querySelector("source")) return;
  const webm = video.getAttribute("data-src-webm");
  const mp4 = video.getAttribute("data-src-mp4");
  if (webm) {
    const sourceWebm = document.createElement("source");
    sourceWebm.src = webm;
    sourceWebm.type = "video/webm";
    video.appendChild(sourceWebm);
  }
  if (mp4) {
    const sourceMp4 = document.createElement("source");
    sourceMp4.src = mp4;
    sourceMp4.type = "video/mp4";
    video.appendChild(sourceMp4);
  }
  video.preload = "auto";
  video.load();
};

previewCards.forEach((card) => {
  const video = card.querySelector("video");
  if (!video) return;

  const resetOtherPreviews = () => {
    previewCards.forEach((otherCard) => {
      if (otherCard === card) return;

      const otherVideo = otherCard.querySelector("video");
      if (!otherVideo) return;

      otherVideo.pause();
      otherVideo.currentTime = 0;
      otherCard.classList.remove("is-playing");
    });
  };

  const playPreview = () => {
    resetOtherPreviews();
    card.classList.add("is-playing");
    ensureVideoSources(video);
    video.play().catch(() => {});
  };

  const stopPreview = () => {
    video.pause();
    video.currentTime = 0;
    video.load(); // Force close socket/connection and release browser decoder
    card.classList.remove("is-playing");
    card.classList.remove("video-playing");
  };

  card.addEventListener("mouseenter", playPreview);
  card.addEventListener("mouseleave", stopPreview);
  card.addEventListener("focusin", playPreview);
  card.addEventListener("focusout", stopPreview);

  // Sync class 'video-playing' when video actually starts/stops rendering frames
  video.addEventListener("playing", () => {
    card.classList.add("video-playing");
  });
  video.addEventListener("pause", () => {
    card.classList.remove("video-playing");
  });
  video.addEventListener("waiting", () => {
    card.classList.remove("video-playing");
  });
  video.addEventListener("seeking", () => {
    card.classList.remove("video-playing");
  });
  video.addEventListener("seeked", () => {
    if (!video.paused) {
      card.classList.add("video-playing");
    }
  });
});

leadForm?.addEventListener("submit", (event) => {
  event.preventDefault();

  const submitButton = leadForm.querySelector("button[type='submit']");
  const originalBtnText = submitButton ? submitButton.textContent : "Получить оценку проекта";
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = "Отправка...";
  }

  const data = new FormData(leadForm);
  const name = data.get("name")?.toString().trim();
  const contact = data.get("contact")?.toString().trim();
  const types = data.getAll("type");
  const message = data.get("message")?.toString().trim() || "Пока без подробностей.";

  // Post to feedback API
  fetch("/api/feedback", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      name: name,
      contact: contact,
      types: types,
      message: message
    })
  })
  .then((response) => {
    if (!response.ok) {
      return response.json().then(errData => { throw new Error(errData.error || "Ошибка отправки"); });
    }
    return response.json();
  })
  .then((res) => {
    if (res.ok) {
      formNote.textContent = "Спасибо! Заявка успешно отправлена. Я свяжусь с вами в ближайшее время.";
      formNote.style.color = "var(--green)";
      leadForm.reset();
    } else {
      throw new Error(res.error || "Неизвестная ошибка сервера");
    }
  })
  .catch((err) => {
    console.error("Feedback API error, falling back to mailto:", err);
    const typesStr = types.map((item) => item.toString()).join(", ") || "Не выбрано";
    const subject = encodeURIComponent("Оценка проекта");
    const body = encodeURIComponent(`Имя: ${name}\nКонтакт: ${contact}\nТип проекта: ${typesStr}\n\nЗадача:\n${message}`);
    window.location.href = `mailto:bul82@yandex.ru?subject=${subject}&body=${body}`;
    formNote.textContent = "Не удалось отправить автоматически. Открываю почтовый клиент...";
    formNote.style.color = "";
  })
  .finally(() => {
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = originalBtnText;
    }
  });
});


// Remove target="_blank" on touch devices (including Telegram iOS/Android webviews)
// to ensure links open reliably within the same browser context/app
if (!window.matchMedia("(pointer: fine)").matches || /Telegram|Instagram|FBAN|FBAV|VKShare/i.test(navigator.userAgent)) {
  document.querySelectorAll('a[target="_blank"]').forEach((link) => {
    const href = link.getAttribute("href");
    if (href && (link.hostname === window.location.hostname || href.startsWith("/") || !href.startsWith("http"))) {
      link.removeAttribute("target");
    }
  });
}

// --- 3D Parallax Tilt & Custom Cursor Logic (Desktop only) ---
if (window.matchMedia("(pointer: fine)").matches) {
  // Prevent native link/image dragging to avoid custom cursor alignment break
  window.addEventListener("dragstart", (e) => {
    e.preventDefault();
  });

  // 1. Create and append cursor elements
  const cursorRing = document.createElement("div");
  cursorRing.className = "custom-cursor-ring";
  const cursorDot = document.createElement("div");
  cursorDot.className = "custom-cursor-dot";
  document.body.appendChild(cursorRing);
  document.body.appendChild(cursorDot);
  
  // Activate custom cursor styling safely
  document.body.classList.add("custom-cursor-active");

  let mouseX = 0, mouseY = 0;
  let ringX = 0, ringY = 0;

  window.addEventListener("mousemove", (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    
    // Position dot immediately
    cursorDot.style.left = `${mouseX}px`;
    cursorDot.style.top = `${mouseY}px`;
  });

  // Smooth trail for the ring
  let cursorRAFId = null;
  function animateCursor() {
    const delay = 6; // lower value = faster following
    ringX += (mouseX - ringX) / delay;
    ringY += (mouseY - ringY) / delay;
    
    cursorRing.style.left = `${ringX}px`;
    cursorRing.style.top = `${ringY}px`;
    
    cursorRAFId = requestAnimationFrame(animateCursor);
  }
  cursorRAFId = requestAnimationFrame(animateCursor);

  // Stop/resume cursor animation when tab is not visible (saves CPU/battery)
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      if (cursorRAFId) cancelAnimationFrame(cursorRAFId);
    } else {
      cursorRAFId = requestAnimationFrame(animateCursor);
    }
  });

  // Attach hover events for links and buttons
  const hoverTargets = document.querySelectorAll("a, button, select, input, textarea, label, [data-menu-toggle]");
  hoverTargets.forEach(el => {
    el.addEventListener("mouseenter", () => {
      cursorRing.classList.add("cursor-hover");
      
      const parentCard = el.closest("[data-accent]");
      if (parentCard) {
        const accentColor = parentCard.getAttribute("data-accent");
        if (accentColor) {
          document.documentElement.style.setProperty('--dynamic-accent', accentColor);
        }
      }
      
      if (el.closest(".case-card") || el.closest(".ai-showcase")) {
        cursorRing.classList.add("cursor-card-hover");
        cursorRing.setAttribute("data-label", "Открыть");
      }
    });
    el.addEventListener("mouseleave", () => {
      cursorRing.classList.remove("cursor-hover");
      cursorRing.classList.remove("cursor-card-hover");
      cursorRing.removeAttribute("data-label");
      
      // Reset accent color
      document.documentElement.style.removeProperty('--dynamic-accent');
    });
  });

  // 2. 3D Parallax Tilt Effect on Case Cards (Desktop only, optimized with static parents to prevent boundary jitter)
  const tiltContainers = document.querySelectorAll(".case-card, .ai-showcase");
  tiltContainers.forEach(container => {
    const target = container.querySelector("a");
    if (!target) return;
    
    let rect = null;
    
    container.addEventListener("mouseenter", () => {
      rect = container.getBoundingClientRect();
      target.style.transition = "transform 0.3s cubic-bezier(0.25, 1, 0.5, 1)";
    });
    
    container.addEventListener("mousemove", (e) => {
      if (!rect) rect = container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const xc = rect.width / 2;
      const yc = rect.height / 2;
      
      // Calculate rotation angles (divided by 90 for an extremely gentle, premium, subtle tilt)
      const angleX = (yc - y) / 90;
      const angleY = (x - xc) / 90;
      
      target.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) scale3d(1.008, 1.008, 1.008)`;
    });
    
    container.addEventListener("mouseleave", () => {
      rect = null;
      target.style.transition = "transform 0.6s cubic-bezier(0.25, 1, 0.5, 1)";
      target.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)";
    });
  });

  // 3. Magnetic Buttons (Desktop only)
  const magneticButtons = document.querySelectorAll(".header-cta, .button");
  magneticButtons.forEach(btn => {
    let rect = null;
    
    btn.addEventListener("mouseenter", () => {
      rect = btn.getBoundingClientRect();
      btn.style.transition = "none";
    });
    
    btn.addEventListener("mousemove", (e) => {
      if (!rect) rect = btn.getBoundingClientRect();
      const x = e.clientX - (rect.left + rect.width / 2);
      const y = e.clientY - (rect.top + rect.height / 2);
      
      btn.style.transform = `translate(${x * 0.35}px, ${y * 0.35}px)`;
    });
    
    btn.addEventListener("mouseleave", () => {
      rect = null;
      btn.style.transition = "transform 0.5s cubic-bezier(0.25, 1, 0.5, 1)";
      btn.style.transform = "";
    });
  });
}

// --- Scroll Progress Bar & Background Parallax Text ---
const progressBar = document.createElement("div");
progressBar.className = "scroll-progress-bar";
document.body.appendChild(progressBar);

// Parallax only on desktop (not needed on mobile, hurts performance)
const isDesktop = window.matchMedia('(min-width: 768px) and (hover: hover)').matches;
const parallaxTexts = isDesktop ? document.querySelectorAll(".bg-parallax-text") : [];

let scrollTicking = false;
window.addEventListener("scroll", () => {
  if (scrollTicking) return;
  scrollTicking = true;
  requestAnimationFrame(() => {
    // 1. Scroll progress bar calculation
    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (scrollHeight > 0) {
      const percentage = (window.scrollY / scrollHeight) * 100;
      progressBar.style.width = `${percentage}%`;
    }

    // 2. Background typography parallax (desktop only)
    if (parallaxTexts.length > 0) {
      const windowHeight = window.innerHeight;
      parallaxTexts.forEach(text => {
        const parent = text.parentElement;
        const rect = parent.getBoundingClientRect();
        if (rect.top < windowHeight && rect.bottom > 0) {
          const speed = parseFloat(text.dataset.speed) || 0.1;
          const relativeScroll = rect.top - windowHeight;
          const translateX = relativeScroll * speed;
          text.style.transform = `translate(calc(-50% + ${translateX}px), -50%)`;
        }
      });
    }
    scrollTicking = false;
  });
}, { passive: true });

// --- Viewport Autoplay for Mobile/Touch ---
if (!window.matchMedia("(pointer: fine)").matches) {
  let playTimeout = null;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const video = entry.target.querySelector("video");
      if (!video) return;

      if (entry.isIntersecting) {
        // Debounce to prevent playing while scrolling quickly
        if (playTimeout) clearTimeout(playTimeout);
        playTimeout = setTimeout(() => {
          // Pause other mobile videos first
          previewCards.forEach(otherCard => {
            if (otherCard === entry.target) return;
            const otherVideo = otherCard.querySelector("video");
            if (otherVideo) {
              otherVideo.pause();
              otherVideo.currentTime = 0;
              otherVideo.load(); // Force close socket/connection
              otherCard.classList.remove("is-playing");
              otherCard.classList.remove("video-playing");
            }
          });

          entry.target.classList.add("is-playing");
          ensureVideoSources(video);
          video.play().catch(() => {});
        }, 300); // 300ms delay: only play if user stops scrolling on this card
      } else {
        if (playTimeout) clearTimeout(playTimeout);
        video.pause();
        video.currentTime = 0;
        video.load(); // Force close socket/connection
        entry.target.classList.remove("is-playing");
        entry.target.classList.remove("video-playing");
      }
    });
  }, {
    root: null,
    rootMargin: "-20% 0px -20% 0px", // triggers in the center 60% of viewport
    threshold: 0.3
  });

  previewCards.forEach(card => observer.observe(card));
}

// --- Window Load Initialization (Instant Page Load + Deferred Video Bind + Staggered Reveal) ---
const revealCards = document.querySelectorAll(".case-card, .ai-showcase");
const triggerReveal = () => {
  if (window.revealsTriggered) return;
  window.revealsTriggered = true;
  revealCards.forEach((card, idx) => {
    setTimeout(() => {
      card.classList.add("revealed");
    }, idx * 80); // 80ms stagger: very crisp, fast, premium feel
  });
};

// Trigger reveal on custom preloader finish event
window.addEventListener("preloader-complete", triggerReveal);

// Fallback: trigger reveal if preloader fails or hangs
setTimeout(triggerReveal, 2500);

window.addEventListener("load", () => {
  // Preload only the very first video in the list to make its hover instant
  const firstVideo = document.querySelector("video[data-src-mp4]");
  if (firstVideo) {
    ensureVideoSources(firstVideo);
  }
});

// Toggle case card details on mobile screens
window.toggleCaseDetails = (event, button) => {
  event.preventDefault();
  event.stopPropagation();
  const card = button.closest('.case-card, .ai-showcase');
  const details = card.querySelector('.case-details');
  const impact = card.querySelector('.case-impact');
  
  // Check current computed display style
  const isHidden = window.getComputedStyle(details).display === 'none';
  
  if (isHidden) {
    details.style.display = 'grid';
    if (impact) impact.style.display = 'grid';
    button.textContent = 'Скрыть детали ▴';
    button.classList.add('active');
  } else {
    details.style.display = 'none';
    if (impact) impact.style.display = 'none';
    button.textContent = 'Детали проекта ▾';
    button.classList.remove('active');
  }
};

// --- Magnetic Spotlight Hover Glow Effect ---
document.querySelectorAll(".metric-grid article, .service-grid article, .price-card, .delivery-grid article").forEach((card) => {
  card.addEventListener("mousemove", (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    card.style.setProperty("--mouse-x", `${x}px`);
    card.style.setProperty("--mouse-y", `${y}px`);
  });
});



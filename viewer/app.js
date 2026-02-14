(function () {
  "use strict";

  const MANIFEST_URL = "./series-manifest.json";

  const refs = {
    seriesSelect: document.getElementById("series-select"),
    sliceRange: document.getElementById("slice-range"),
    sliceLabel: document.getElementById("slice-label"),
    prevBtn: document.getElementById("prev-btn"),
    nextBtn: document.getElementById("next-btn"),
    seriesDescription: document.getElementById("series-description"),
    combinedImage: document.getElementById("combined-image"),
    combinedCaption: document.getElementById("combined-caption")
  };

  const state = {
    series: [],
    selectedSeriesIndex: 0,
    currentSlice: 0
  };

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function currentSeries() {
    return state.series[state.selectedSeriesIndex];
  }

  function formatSlice(slice, total, startIndex) {
    const current = startIndex + slice + 1;
    return `${slice + 1} / ${total} (absolute index ${current})`;
  }

  function resolvePattern(pattern, absoluteIndex) {
    return pattern
      .replaceAll("{index}", String(absoluteIndex))
      .replaceAll("{indexPadded}", String(absoluteIndex).padStart(3, "0"));
  }

  function isAbsolutePath(path) {
    return path.startsWith("http://") || path.startsWith("https://") || path.startsWith("/") || path.startsWith("data:");
  }

  function joinPath(basePath, filePath) {
    if (!basePath || isAbsolutePath(filePath)) {
      return filePath;
    }
    const base = basePath.endsWith("/") ? basePath.slice(0, -1) : basePath;
    const file = filePath.startsWith("/") ? filePath.slice(1) : filePath;
    return `${base}/${file}`;
  }

  function createImageUrl(series, absoluteIndex, sliceIndex) {
    if (series.images.length > 0) {
      return series.images[sliceIndex] || "";
    }
    if (series.image) {
      return series.image;
    }
    if (!series.imagePattern) {
      return "";
    }
    return resolvePattern(series.imagePattern, absoluteIndex);
  }

  function setImageWithFallback(imgEl, url, captionBase) {
    if (!url) {
      imgEl.removeAttribute("src");
      refs.combinedCaption.textContent = `${captionBase}: no source configured`;
      return;
    }

    imgEl.onerror = function () {
      refs.combinedCaption.textContent = `${captionBase}: failed to load`;
    };
    imgEl.onload = function () {
      refs.combinedCaption.textContent = captionBase;
    };
    imgEl.src = url;
  }

  function preloadAdjacentSlices(series, sliceIndex) {
    const candidates = [sliceIndex - 1, sliceIndex + 1];
    for (const candidateSlice of candidates) {
      if (candidateSlice < 0 || candidateSlice >= series.slices) {
        continue;
      }
      const candidateAbsoluteIndex = series.startIndex + candidateSlice;
      const url = createImageUrl(series, candidateAbsoluteIndex, candidateSlice);
      if (!url) {
        continue;
      }
      const probe = new Image();
      probe.src = url;
    }
  }

  function render() {
    const series = currentSeries();
    if (!series) {
      return;
    }

    const absoluteIndex = series.startIndex + state.currentSlice;
    refs.sliceRange.max = String(series.slices - 1);
    refs.sliceRange.value = String(state.currentSlice);
    refs.sliceLabel.textContent = formatSlice(state.currentSlice, series.slices, series.startIndex);
    refs.seriesDescription.textContent = series.description || "";

    const imageUrl = createImageUrl(series, absoluteIndex, state.currentSlice);
    setImageWithFallback(refs.combinedImage, imageUrl, `Slice ${absoluteIndex}`);

    preloadAdjacentSlices(series, state.currentSlice);
  }

  function changeSlice(delta) {
    const series = currentSeries();
    state.currentSlice = clamp(state.currentSlice + delta, 0, series.slices - 1);
    render();
  }

  function onWheel(event) {
    event.preventDefault();
    const step = event.deltaY > 0 ? 1 : -1;
    changeSlice(step);
  }

  function onKeyDown(event) {
    if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
      event.preventDefault();
      changeSlice(-1);
      return;
    }
    if (event.key === "ArrowRight" || event.key === "ArrowDown") {
      event.preventDefault();
      changeSlice(1);
    }
  }

  function validateAndNormalizeSeries(series) {
    return series.map((entry, index) => {
      const imagePattern = entry.imagePattern || "";
      const image = entry.image || "";
      const imageBasePath = entry.imageBasePath || "";
      const images =
        Array.isArray(entry.images) && entry.images.length > 0
          ? entry.images.map(function (filePath) {
              if (typeof filePath !== "string" || filePath.length === 0) {
                throw new Error(`Invalid image path in series at index ${index}`);
              }
              return joinPath(imageBasePath, filePath);
            })
          : [];

      const hasPerSliceImages = images.length > 0;
      const hasPattern = imagePattern.length > 0;
      const hasStaticImage = image.length > 0;
      if (!entry.id || !entry.label || (!hasPerSliceImages && !hasPattern && !hasStaticImage)) {
        throw new Error(`Invalid series at index ${index}`);
      }

      const parsedSlices = Number(entry.slices);
      let slices = Number.isFinite(parsedSlices) && parsedSlices > 0 ? parsedSlices : 0;
      if (slices === 0 && hasPerSliceImages) {
        slices = images.length;
      }
      if (slices === 0 && hasStaticImage) {
        slices = 1;
      }
      if (slices <= 0) {
        throw new Error(`Series at index ${index} needs a valid 'slices' value`);
      }
      if (hasPerSliceImages && slices !== images.length) {
        throw new Error(`Series at index ${index} has 'slices' != images.length`);
      }

      const startIndex = Number.isFinite(Number(entry.startIndex)) ? Number(entry.startIndex) : 0;
      const endIndex = startIndex + slices - 1;

      return {
        id: entry.id,
        label: entry.label,
        description: entry.description || "",
        slices,
        startIndex,
        endIndex,
        imagePattern,
        image,
        images
      };
    });
  }

  async function loadManifest() {
    const response = await fetch(MANIFEST_URL, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Manifest request failed: ${response.status}`);
    }
    const data = await response.json();
    if (!Array.isArray(data.series)) {
      throw new Error("Manifest must contain a 'series' array");
    }
    state.series = validateAndNormalizeSeries(data.series);
  }

  function populateSeriesSelect() {
    refs.seriesSelect.innerHTML = "";
    state.series.forEach((entry, index) => {
      const opt = document.createElement("option");
      opt.value = String(index);
      opt.textContent = entry.label;
      refs.seriesSelect.appendChild(opt);
    });
  }

  function bindUI() {
    refs.seriesSelect.addEventListener("change", function (event) {
      state.selectedSeriesIndex = Number(event.target.value);
      state.currentSlice = 0;
      render();
    });

    refs.sliceRange.addEventListener("input", function (event) {
      state.currentSlice = Number(event.target.value);
      render();
    });

    refs.prevBtn.addEventListener("click", function () {
      changeSlice(-1);
    });

    refs.nextBtn.addEventListener("click", function () {
      changeSlice(1);
    });

    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("wheel", onWheel, { passive: false });
  }

  function showFatal(message) {
    const text = `Viewer setup error: ${message}`;
    refs.seriesDescription.textContent = text;
    refs.combinedCaption.textContent = text;
  }

  async function init() {
    try {
      await loadManifest();
      if (state.series.length === 0) {
        throw new Error("Manifest includes zero series");
      }
      populateSeriesSelect();
      bindUI();
      render();
    } catch (error) {
      showFatal(error.message);
    }
  }

  init();
})();

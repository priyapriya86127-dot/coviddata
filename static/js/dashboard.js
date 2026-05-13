(function () {
  const el = document.getElementById("dashboard-data");
  if (!el) return;
  const data = JSON.parse(el.textContent);

  const themeColors = {
    purple: "#9d7af5",
    green: "#4ade80",
    blue: "#3d9cfd",
    red: "#f87171",
    yellow: "#fbbf24",
  };

  function sparklineOptions(color) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales: {
        x: { display: false },
        y: { display: false },
      },
      elements: {
        line: { borderWidth: 2, tension: 0.35 },
        point: { radius: 0, hoverRadius: 0 },
      },
    };
  }

  data.summary.forEach(function (row, i) {
    const canvas = document.getElementById("spark-" + i);
    if (!canvas || typeof Chart === "undefined") return;
    const c = themeColors[row.theme] || themeColors.purple;
    const vals = row.sparkline || [];
    new Chart(canvas.getContext("2d"), {
      type: "line",
      data: {
        labels: vals.map(function (_, j) {
          return j;
        }),
        datasets: [
          {
            data: vals,
            borderColor: c,
            backgroundColor: "transparent",
            fill: false,
          },
        ],
      },
      options: sparklineOptions(c),
    });
  });

  const trendCtx = document.getElementById("chart-trends");
  if (trendCtx && data.trends) {
    const t = data.trends;
    new Chart(trendCtx.getContext("2d"), {
      type: "line",
      data: {
        labels: t.labels,
        datasets: [
          {
            label: "Cases",
            data: t.cases,
            borderColor: themeColors.purple,
            backgroundColor: "rgba(157, 122, 245, 0.1)",
            fill: true,
            tension: 0.35,
          },
          {
            label: "Recovered",
            data: t.recovered,
            borderColor: themeColors.green,
            backgroundColor: "transparent",
            tension: 0.35,
          },
          {
            label: "Deaths",
            data: t.deaths,
            borderColor: themeColors.red,
            backgroundColor: "transparent",
            tension: 0.35,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: {
            position: "top",
            labels: { color: "#8b9cb3", boxWidth: 12 },
          },
        },
        scales: {
          x: {
            ticks: { color: "#8b9cb3", maxRotation: 45 },
            grid: { color: "rgba(255,255,255,0.06)" },
          },
          y: {
            ticks: { color: "#8b9cb3" },
            grid: { color: "rgba(255,255,255,0.06)" },
          },
        },
      },
    });

    document.querySelectorAll(".chart-tabs button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (btn.disabled) return;
        document.querySelectorAll(".chart-tabs button").forEach(function (b) {
          b.classList.toggle("is-on", b === btn);
        });
      });
    });
  }

  const donutCtx = document.getElementById("chart-vax");
  if (donutCtx && data.vaccination) {
    const v = data.vaccination;
    const pop = v["Total Population"] || 1;
    const full = v["Fully Vaccinated"] || 0;
    const part = v["Partially Vaccinated"] || 0;
    const boost = v["Booster Doses"] || 0;
    const other = Math.max(0, pop - full - part);

    new Chart(donutCtx.getContext("2d"), {
      type: "doughnut",
      data: {
        labels: ["Fully vaccinated", "Partially", "Other"],
        datasets: [
          {
            data: [full, part, other],
            backgroundColor: [
              themeColors.blue,
              themeColors.purple,
              "#2d3a4a",
            ],
            borderWidth: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "68%",
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: "#8b9cb3", boxWidth: 10, font: { size: 11 } },
          },
        },
      },
    });
  }

  const mapEl = document.getElementById("map-global");
  if (mapEl && data.map && typeof Plotly !== "undefined") {
    Plotly.newPlot(
      mapEl,
      [
        {
          type: "choropleth",
          locationmode: "country names",
          locations: data.map.locations,
          z: data.map.values,
          colorscale: [
            [0, "#1a1030"],
            [0.35, "#4a2d7a"],
            [0.65, "#7c4dff"],
            [1, "#e0b0ff"],
          ],
          colorbar: {
            title: "Cases",
            tickfont: { color: "#8b9cb3" },
            titlefont: { color: "#8b9cb3" },
          },
          marker: { line: { color: "#0a0e14", width: 0.5 } },
        },
      ],
      {
        margin: { t: 10, b: 10, l: 10, r: 10 },
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        geo: {
          bgcolor: "transparent",
          showland: true,
          landcolor: "#121a24",
          showocean: true,
          oceancolor: "#0a0e14",
          projection: { type: "natural earth" },
          showlakes: true,
          lakecolor: "#0a0e14",
          coastlinewidth: 0.3,
        },
        font: { color: "#8b9cb3" },
      },
      { responsive: true, displayModeBar: false }
    );
  }

  const tbody = document.querySelector("#country-tbody");
  const pager = document.querySelector("#table-pager");
  if (tbody && data.countries) {
    const pageSize = 5;
    const rows = data.countries;
    const pages = Math.max(1, Math.ceil(rows.length / pageSize));
    let page = 0;

    function fmt(n) {
      if (n >= 1e9) return (n / 1e9).toFixed(2) + "B";
      if (n >= 1e6) return (n / 1e6).toFixed(2) + "M";
      if (n >= 1e3) return (n / 1e3).toFixed(2) + "K";
      return n.toLocaleString();
    }

    function render() {
      tbody.innerHTML = "";
      const start = page * pageSize;
      rows.slice(start, start + pageSize).forEach(function (r) {
        const tr = document.createElement("tr");
        const fc = r.flag_code || "un";
        tr.innerHTML =
          '<td><div class="country-cell"><img src="https://flagcdn.com/w40/' +
          fc +
          '.png" alt="" width="40" height="30" loading="lazy" />' +
          r.country +
          "</div></td>" +
          '<td class="num">' +
          fmt(r.total_cases) +
          "</td>" +
          '<td class="num">' +
          fmt(r.deaths) +
          "</td>" +
          '<td class="num">' +
          fmt(r.recovered) +
          "</td>";
        tbody.appendChild(tr);
      });
      if (pager) {
        pager.innerHTML = "";
        for (let i = 0; i < pages; i++) {
          const b = document.createElement("button");
          b.type = "button";
          b.textContent = String(i + 1);
          if (i === page) b.classList.add("is-cur");
          b.addEventListener("click", function () {
            page = i;
            render();
          });
          pager.appendChild(b);
        }
      }
    }
    render();
  }
})();

(function () {
  const layout = document.getElementById("dashboard-layout");
  const sidebar = document.getElementById("dashboard-sidebar");
  const backdrop = document.getElementById("sidebar-backdrop");
  const toggle = document.querySelector(".sidebar-toggle");
  const closeBtn = document.querySelector(".sidebar-close");
  if (!layout || !sidebar || !toggle) return;

  function isDrawerMode() {
    return window.matchMedia("(max-width: 960px)").matches;
  }

  function setOpen(open) {
    if (!isDrawerMode()) {
      layout.classList.remove("nav-drawer-open");
      document.body.classList.remove("nav-drawer-locked");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Open navigation menu");
      if (backdrop) backdrop.setAttribute("aria-hidden", "true");
      return;
    }
    layout.classList.toggle("nav-drawer-open", open);
    document.body.classList.toggle("nav-drawer-locked", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "Close navigation menu" : "Open navigation menu");
    if (backdrop) backdrop.setAttribute("aria-hidden", open ? "false" : "true");
  }

  function closeMenu() {
    setOpen(false);
  }

  toggle.addEventListener("click", function () {
    setOpen(!layout.classList.contains("nav-drawer-open"));
  });

  if (backdrop) {
    backdrop.addEventListener("click", closeMenu);
  }
  if (closeBtn) {
    closeBtn.addEventListener("click", closeMenu);
  }

  sidebar.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () {
      if (isDrawerMode()) closeMenu();
    });
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && layout.classList.contains("nav-drawer-open")) {
      closeMenu();
    }
  });

  window.matchMedia("(min-width: 961px)").addEventListener("change", function (e) {
    if (e.matches) closeMenu();
  });

  window.addEventListener("resize", function () {
    const mapEl = document.getElementById("map-global");
    if (mapEl && typeof Plotly !== "undefined") {
      try {
        Plotly.Plots.resize(mapEl);
      } catch (err) {
        /* ignore */
      }
    }
  });
})();

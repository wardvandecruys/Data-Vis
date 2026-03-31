# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 17:00:41 2026

@author: ward_
"""

import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    from math import pi

    from bokeh.models import ColumnDataSource, HoverTool, CustomJS
    from bokeh.plotting import figure

    return ColumnDataSource, CustomJS, HoverTool, figure, np, pd, pi


@app.cell
def _(np, pd, pi):
    rng = np.random.default_rng(42)

    # 15 datapoints using 9 community IDs, with repeats by design
    community_ids = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3, 4, 6, 8])
    rng.shuffle(community_ids)

    n = len(community_ids)

    # Fake lon/lat clustered in a small geographic window
    lon = rng.uniform(4.20, 4.60, n)
    lat = rng.uniform(50.78, 51.02, n)

    # Coverage between 10% and 90%
    coverage_pct = rng.integers(10, 91, n)

    # Water depth between 0 and 15 cm
    water_depth_cm = np.round(rng.uniform(0, 15, n), 1)

    # Community colors (same community = same color)
    palette = {
        1: "#1f77b4",
        2: "#ff7f0e",
        3: "#2ca02c",
        4: "#d62728",
        5: "#9467bd",
        6: "#8c564b",
        7: "#e377c2",
        8: "#17becf",
        9: "#bcbd22",
    }

    band_color = [palette[c] for c in community_ids]

    # Start ring at the top and sweep clockwise-ish around full circle
    start_angle = np.repeat(pi / 2, n)
    end_angle = start_angle + 2 * pi * (coverage_pct / 100.0)

    df = pd.DataFrame(
        {
            "site_id": [f"S{i:02d}" for i in range(1, n + 1)],
            "community_id": community_ids,
            "community_text": community_ids.astype(str),
            "lon": lon,
            "lat": lat,
            "coverage_pct": coverage_pct,
            "water_depth_cm": water_depth_cm,
            "water_text": [f"💧 {v:.1f} cm" for v in water_depth_cm],
            "start_angle": start_angle,
            "end_angle": end_angle,
            # Slight offset for the water-depth label
            "drop_lon": lon + 0.012,
            "drop_lat": lat + 0.008,
            # Mutable visual columns
            "inner_r": np.repeat(11, n),
            "outer_r": np.repeat(18, n),
            "core_size": np.repeat(24, n),
            "hit_size": np.repeat(36, n),
            "text_size": np.repeat("11pt", n),
            "drop_size": np.repeat("9pt", n),
            "glyph_alpha": np.repeat(1.0, n),
            "fill_color": np.repeat("#ffffff", n),
            "band_color": band_color,
            "text_color": np.repeat("#111111", n),
            "drop_color": np.repeat("#1f4e79", n),
            # Base visual columns for restoring after selection reset
            "base_inner_r": np.repeat(11, n),
            "base_outer_r": np.repeat(18, n),
            "base_core_size": np.repeat(24, n),
            "base_hit_size": np.repeat(36, n),
            "base_text_size": np.repeat("11pt", n),
            "base_drop_size": np.repeat("9pt", n),
            "base_glyph_alpha": np.repeat(1.0, n),
            "base_fill_color": np.repeat("#ffffff", n),
            "base_band_color": band_color,
            "base_text_color": np.repeat("#111111", n),
            "base_drop_color": np.repeat("#1f4e79", n),
        }
    )

    df
    return (df,)


@app.cell
def _(ColumnDataSource, CustomJS, HoverTool, df, figure):
    source = ColumnDataSource(df)

    p = figure(
        width=980,
        height=620,
        title="Prototype community-site glyph map",
        tools="pan,wheel_zoom,reset,save,tap",
        active_scroll="wheel_zoom",
        match_aspect=True,
        toolbar_location="right",
    )

    p.xaxis.axis_label = "Longitude"
    p.yaxis.axis_label = "Latitude"
    p.grid.grid_line_alpha = 0.20

    # Background ring (full grey circle)
    p.annular_wedge(
        x="lon",
        y="lat",
        inner_radius="inner_r",
        outer_radius="outer_r",
        start_angle=0,
        end_angle=2 * 3.141592653589793,
        inner_radius_units="screen",
        outer_radius_units="screen",
        fill_color="#e5e7eb",
        line_color=None,
        source=source,
    )

    # Coverage ring
    p.annular_wedge(
        x="lon",
        y="lat",
        inner_radius="inner_r",
        outer_radius="outer_r",
        start_angle="start_angle",
        end_angle="end_angle",
        inner_radius_units="screen",
        outer_radius_units="screen",
        fill_color="band_color",
        line_color=None,
        fill_alpha="glyph_alpha",
        source=source,
    )

    # White center
    p.circle(
        x="lon",
        y="lat",
        size="core_size",
        fill_color="fill_color",
        line_color="band_color",
        line_width=1.5,
        fill_alpha="glyph_alpha",
        line_alpha="glyph_alpha",
        source=source,
    )

    # Community ID text in the middle
    p.text(
        x="lon",
        y="lat",
        text="community_text",
        text_align="center",
        text_baseline="middle",
        text_font_size="text_size",
        text_font_style="bold",
        text_color="text_color",
        text_alpha="glyph_alpha",
        source=source,
    )

    # Water-depth "raindrop" label
    p.text(
        x="drop_lon",
        y="drop_lat",
        text="water_text",
        text_font_size="drop_size",
        text_color="drop_color",
        text_alpha="glyph_alpha",
        source=source,
    )

    # Invisible hit area for easier hover/tap
    hit_renderer = p.circle(
        x="lon",
        y="lat",
        size="hit_size",
        fill_alpha=0.0,
        line_alpha=0.0,
        source=source,
    )

    hover = HoverTool(
        renderers=[hit_renderer],
        tooltips=[
            ("Site", "@site_id"),
            ("Community", "@community_id"),
            ("Coverage", "@coverage_pct%"),
            ("Water depth", "@water_depth_cm cm"),
            ("Lon", "@lon{0.000}"),
            ("Lat", "@lat{0.000}"),
        ],
    )
    p.add_tools(hover)

    callback = CustomJS(
        args=dict(source=source),
        code="""
        const d = source.data;
        const idxs = source.selected.indices;
        const n = d["community_id"].length;

        function restore_all() {
            for (let i = 0; i < n; i++) {
                d["inner_r"][i]     = d["base_inner_r"][i];
                d["outer_r"][i]     = d["base_outer_r"][i];
                d["core_size"][i]   = d["base_core_size"][i];
                d["hit_size"][i]    = d["base_hit_size"][i];
                d["text_size"][i]   = d["base_text_size"][i];
                d["drop_size"][i]   = d["base_drop_size"][i];
                d["glyph_alpha"][i] = d["base_glyph_alpha"][i];
                d["fill_color"][i]  = d["base_fill_color"][i];
                d["band_color"][i]  = d["base_band_color"][i];
                d["text_color"][i]  = d["base_text_color"][i];
                d["drop_color"][i]  = d["base_drop_color"][i];
            }
        }

        if (idxs.length === 0) {
            restore_all();
            source.change.emit();
            return;
        }

        const selected_idx = idxs[0];
        const selected_community = d["community_id"][selected_idx];

        for (let i = 0; i < n; i++) {
            const same = d["community_id"][i] === selected_community;

            if (same) {
                d["inner_r"][i]     = d["base_inner_r"][i] * 1.35;
                d["outer_r"][i]     = d["base_outer_r"][i] * 1.35;
                d["core_size"][i]   = d["base_core_size"][i] * 1.35;
                d["hit_size"][i]    = d["base_hit_size"][i] * 1.35;
                d["text_size"][i]   = "14pt";
                d["drop_size"][i]   = "11pt";
                d["glyph_alpha"][i] = 1.0;
                d["fill_color"][i]  = "#ffffff";
                d["band_color"][i]  = d["base_band_color"][i];
                d["text_color"][i]  = "#000000";
                d["drop_color"][i]  = "#1f4e79";
            } else {
                d["inner_r"][i]     = d["base_inner_r"][i] * 0.75;
                d["outer_r"][i]     = d["base_outer_r"][i] * 0.75;
                d["core_size"][i]   = d["base_core_size"][i] * 0.75;
                d["hit_size"][i]    = d["base_hit_size"][i] * 0.75;
                d["text_size"][i]   = "9pt";
                d["drop_size"][i]   = "8pt";
                d["glyph_alpha"][i] = 0.28;
                d["fill_color"][i]  = "#f0f0f0";
                d["band_color"][i]  = "#bdbdbd";
                d["text_color"][i]  = "#7a7a7a";
                d["drop_color"][i]  = "#9a9a9a";
            }
        }

        source.change.emit();
        """,
    )

    source.selected.js_on_change("indices", callback)

    p.legend.visible = False
    p
    return


if __name__ == "__main__":
    app.run()

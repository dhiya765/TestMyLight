import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from math import sqrt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# -----------------------
# Page config
# -----------------------
st.set_page_config(page_title="TestMyLight", layout="wide")

# -----------------------
# Functional groups table
# -----------------------
FG_TABLE = pd.DataFrame([
    {"Group": "O–H (alcohol)", "Range_min": 3200, "Range_max": 3600, "Notes": "broad"},
    {"Group": "O–H (acid)",    "Range_min": 2500, "Range_max": 3300, "Notes": "very broad"},
    {"Group": "N–H",           "Range_min": 3300, "Range_max": 3500, "Notes": "sharp/medium"},
    {"Group": "C–H (sp3)",     "Range_min": 2850, "Range_max": 2960, "Notes": "alkanes"},
    {"Group": "C–H (sp2)",     "Range_min": 3000, "Range_max": 3100, "Notes": "alkenes/aromatics"},
    {"Group": "C=O",           "Range_min": 1650, "Range_max": 1750, "Notes": "strong"},
    {"Group": "Amide I",       "Range_min": 1600, "Range_max": 1700, "Notes": "proteins"},
    {"Group": "Amide II",      "Range_min": 1480, "Range_max": 1580, "Notes": "proteins"},
    {"Group": "C=C (aromatic)","Range_min": 1450, "Range_max": 1600, "Notes": ""},
    {"Group": "C–O",           "Range_min": 1000, "Range_max": 1300, "Notes": "alcohol/ether"},
    {"Group": "P=O",           "Range_min": 1100, "Range_max": 1250, "Notes": "phosphate"},
    {"Group": "S=O",           "Range_min": 1030, "Range_max": 1200, "Notes": "sulphate"},
])

# -----------------------
# Styling
# -----------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #f7f9fc;
        font-size: 18px;
    }

    section[data-testid="stSidebar"] {
        background-color: #eaf4f4;
    }

    html, body, [class*="css"]  {
        font-size: 18px;
    }

    p, li, label, div {
        font-size: 18px !important;
    }

    h1 {
        color: #5c7c8a;
        font-size: 3rem !important;
        font-weight: 700;
    }

    h2, h3 {
        color: #6d8f9b;
        font-size: 1.8rem !important;
    }

    .stButton > button {
        background-color: #cde7e7;
        color: black;
        border-radius: 10px;
        border: none;
        font-size: 17px;
        padding: 0.5rem 1rem;
    }

    .stButton > button:hover {
        background-color: #b5dcdc;
    }

    .welcome-box {
        background-color: #eef6f6;
        padding: 1.2rem;
        border-radius: 14px;
        margin-bottom: 1rem;
        font-size: 18px;
        color: #3d5560;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------
# Load data
# -----------------------
@st.cache_data
def load_data():
    file = "PreparedDatasetATRFTIR.xlsx"
    sheets = pd.read_excel(file, sheet_name=None)
    return sheets

data = load_data()

# -----------------------
# Sidebar
# -----------------------
st.sidebar.markdown("## TestMyLight Control")
group_id = st.sidebar.text_input("Group ID")

dataset_name = st.sidebar.selectbox(
    "Select Dataset",
    list(data.keys())
)

df = data[dataset_name].copy()
df.columns = [str(c).strip() for c in df.columns]

page = st.sidebar.radio(
    "Page",
    ["Home", "Explore", "Plot", "Interpret", "Classify", "Dashboard"]
)

# =======================
# HOME
# =======================
if page == "Home":
    st.title("TestMyLight 🌿")
    st.subheader("Interactive spectroscopy exploration for workshop learning")

    st.markdown("""
    <div class="welcome-box">
    <b>Welcome to TestMyLight.</b><br><br>
    In this workshop, you will explore ATR-FTIR spectra from algae samples, standards, and mixtures.
    Your task is to compare spectra, zoom into important regions, inspect the data table, and make
    evidence-based decisions about sample identity and composition.
    <br><br>
    You will learn to:
    <ul>
        <li>compare pure and mixed samples,</li>
        <li>identify useful spectral regions,</li>
        <li>interpret similarities and differences,</li>
        <li>classify samples with confidence.</li>
    </ul>
    Start by choosing a dataset from the sidebar, then move to <b>Explore</b> or <b>Plot</b>.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Example spectrum")

    if len(df.columns) > 1:
        wn_col = df.columns[0]
        spectra_cols = list(df.columns[1:])

        preview_cols = spectra_cols[:min(3, len(spectra_cols))]
        fig = go.Figure()

        x = pd.to_numeric(df[wn_col], errors="coerce")

        for col in preview_cols:
            y = pd.to_numeric(df[col], errors="coerce")
            mask = x.notna() & y.notna()

            fig.add_trace(go.Scatter(
                x=x[mask],
                y=y[mask],
                mode="lines",
                name=str(col)
            ))

        fig.update_layout(
            title="Preview of selected dataset spectra",
            xaxis_title=str(wn_col),
            yaxis_title="Intensity",
            hovermode="x unified",
            height=450
        )
        fig.update_xaxes(autorange="reversed")

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No spectra available to preview.")

# =======================
# EXPLORE
# =======================
elif page == "Explore":
    st.header("Data Explorer")
    st.write(f"**Selected dataset:** {dataset_name}")
    st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")

    try:
        st.subheader("Column names")
        st.write(list(df.columns))

        st.subheader("Preview")
        st.dataframe(df.head(20), use_container_width=True)

        with st.expander("Show data types"):
            dtypes_df = pd.DataFrame({
                "Column": df.columns,
                "Type": [str(t) for t in df.dtypes]
            })
            st.dataframe(dtypes_df, use_container_width=True)

        with st.expander("Show missing values"):
            missing_df = pd.DataFrame({
                "Column": df.columns,
                "Missing values": df.isna().sum().values
            })
            st.dataframe(missing_df, use_container_width=True)

    except Exception as e:
        st.error(f"Could not display this sheet directly: {e}")
        st.subheader("Raw fallback preview")
        try:
            st.write(df.head(10).to_dict())
        except Exception as e2:
            st.error(f"Fallback preview also failed: {e2}")

# =======================
# PLOT
# =======================
elif page == "Plot":
    st.header("Spectra Plot")
    st.write(f"**Dataset:** {dataset_name}")

    if len(df.columns) < 2:
        st.warning("No spectra columns found to plot.")
    else:
        df_plot = df.copy()
        wn_col = df_plot.columns[0]
        spectra_cols = list(df_plot.columns[1:])

        st.write(f"**Detected wavenumber column:** {wn_col}")

        default_cols = spectra_cols[:min(3, len(spectra_cols))]
        selected_cols = st.multiselect(
            "Select spectra to plot",
            spectra_cols,
            default=default_cols
        )

        normalize = st.checkbox("Normalize spectra for comparison", value=False)
        show_table = st.checkbox("Show numeric preview", value=False)

        if selected_cols:
            plot_df = df_plot[[wn_col] + selected_cols].copy()
            plot_df[wn_col] = pd.to_numeric(plot_df[wn_col], errors="coerce")
            plot_df = plot_df.dropna(subset=[wn_col])
            plot_df = plot_df.sort_values(by=wn_col, ascending=False)

            fig = go.Figure()

            for col in selected_cols:
                y = pd.to_numeric(plot_df[col], errors="coerce")
                mask = y.notna()
                y = y[mask]
                x = plot_df.loc[mask, wn_col]

                if normalize:
                    y_min = y.min()
                    y_max = y.max()
                    if pd.notna(y_min) and pd.notna(y_max) and y_max != y_min:
                        y = (y - y_min) / (y_max - y_min)

                fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    mode="lines",
                    name=str(col)
                ))

            fig.update_layout(
                title="Spectra Comparison",
                xaxis_title=str(wn_col),
                yaxis_title="Normalized Intensity" if normalize else "Intensity",
                hovermode="x unified",
                height=550
            )

            fig.update_xaxes(autorange="reversed")

            st.markdown("### Functional groups reference")
            st.dataframe(
                FG_TABLE.rename(columns={
                    "Range_min": "Start (cm⁻¹)",
                    "Range_max": "End (cm⁻¹)"
                }),
                use_container_width=True
            )

            selected_groups = st.multiselect(
                "Select functional groups to highlight on the spectrum",
                FG_TABLE["Group"].tolist()
            )

            for g in selected_groups:
                row = FG_TABLE[FG_TABLE["Group"] == g].iloc[0]
                fig.add_vrect(
                    x0=row["Range_min"],
                    x1=row["Range_max"],
                    fillcolor="LightSalmon",
                    opacity=0.25,
                    layer="below",
                    line_width=0
                )

            st.plotly_chart(fig, use_container_width=True)

            if show_table:
                st.subheader("Preview of plotted values")
                st.dataframe(plot_df.head(20), use_container_width=True)
        else:
            st.info("Select at least one spectrum column.")

# =======================
# INTERPRET
# =======================
elif page == "Interpret":
    st.header("Interpretation")
    st.write(f"**Dataset:** {dataset_name}")

    if len(df.columns) < 2:
        st.warning("No spectra available for interpretation.")
    else:
        wn_col = df.columns[0]
        sample_options = list(df.columns[1:])

        selected_sample = st.selectbox("Select sample", sample_options)
        comparison_options = ["None"] + sample_options
        comparison_sample = st.selectbox("Compare with", comparison_options)

        wn_values = pd.to_numeric(df[wn_col], errors="coerce").dropna()

        region_start, region_end = st.slider(
            "Select important spectral region",
            min_value=int(wn_values.min()),
            max_value=int(wn_values.max()),
            value=(1500, 1700)
        )

        if selected_sample:
            fig_preview = go.Figure()

            x = pd.to_numeric(df[wn_col], errors="coerce")
            y = pd.to_numeric(df[selected_sample], errors="coerce")
            mask = x.notna() & y.notna()

            fig_preview.add_trace(go.Scatter(
                x=x[mask],
                y=y[mask],
                mode="lines",
                name=selected_sample
            ))

            if comparison_sample != "None":
                y2 = pd.to_numeric(df[comparison_sample], errors="coerce")
                mask2 = x.notna() & y2.notna()

                fig_preview.add_trace(go.Scatter(
                    x=x[mask2],
                    y=y2[mask2],
                    mode="lines",
                    name=comparison_sample
                ))

            fig_preview.update_layout(
                title=f"Preview: {selected_sample}",
                xaxis_title="Wavenumber (cm⁻¹)",
                yaxis_title="Intensity",
                height=450
            )

            fig_preview.add_vrect(
                x0=region_start,
                x1=region_end,
                fillcolor="LightSalmon",
                opacity=0.25,
                layer="below",
                line_width=0,
                annotation_text="Selected region",
                annotation_position="top left"
            )

            fig_preview.update_xaxes(autorange="reversed")
            st.plotly_chart(fig_preview, use_container_width=True)

            st.info("Tip: Look for strong peaks and compare their positions with known functional group regions.")
            st.caption("Hint: Around 1650–1550 cm⁻¹ may indicate amide bands (proteins).")

        suspected_groups = st.multiselect(
            "Suspected functional groups",
            FG_TABLE["Group"].tolist()
        )

        confidence = st.selectbox(
            "How confident are you?",
            ["Low", "Medium", "High"]
        )

        interpretation = st.text_area(
            "Interpretation",
            placeholder="Write a short interpretation of what the spectrum suggests and why."
        )

        with st.expander("Functional groups reference"):
            st.dataframe(
                FG_TABLE.rename(columns={
                    "Range_min": "Start (cm⁻¹)",
                    "Range_max": "End (cm⁻¹)"
                }),
                use_container_width=True
            )

        if st.button("Save interpretation"):
            row = {
                "time": datetime.now(),
                "group": group_id,
                "dataset": dataset_name,
                "page": "Interpret",
                "sample": selected_sample,
                "comparison_sample": comparison_sample,
                "important_region": f"{region_start}-{region_end}",
                "suspected_groups": "; ".join(suspected_groups),
                "confidence": confidence,
                "interpretation": interpretation
            }

            pd.DataFrame([row]).to_csv(
                "responses.csv",
                mode="a",
                header=not pd.io.common.file_exists("responses.csv"),
                index=False
            )

            st.success("Interpretation saved.")

# =======================
# CLASSIFY
# =======================
elif page == "Classify":
    st.header("Classification")
    st.write(f"**Dataset:** {dataset_name}")

    if len(df.columns) < 3:
        st.warning("Not enough spectra available for PCA.")
    else:
        wn_col = df.columns[0]
        sample_cols = list(df.columns[1:])

        target_sample = st.selectbox("Select sample to classify", sample_cols)

        X = df[[wn_col] + sample_cols].copy()
        X[wn_col] = pd.to_numeric(X[wn_col], errors="coerce")
        X = X.dropna(subset=[wn_col])

        spectra_only = X[sample_cols].apply(pd.to_numeric, errors="coerce")
        X_pca = spectra_only.T
        X_pca = X_pca.dropna(axis=1, how="any")

        if X_pca.shape[1] < 2:
            st.warning("Not enough clean numeric features available for PCA.")
        else:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_pca)

            pca = PCA(n_components=2)
            pcs = pca.fit_transform(X_scaled)

            pca_df = pd.DataFrame({
                "sample": X_pca.index,
                "PC1": pcs[:, 0],
                "PC2": pcs[:, 1]
            })

            pca_df["highlight"] = pca_df["sample"].apply(
                lambda s: "Selected sample" if s == target_sample else "Other samples"
            )

            fig = px.scatter(
                pca_df,
                x="PC1",
                y="PC2",
                color="highlight",
                text="sample",
                title="PCA of selected dataset"
            )

            fig.update_traces(textposition="top center")
            fig.update_layout(height=500)
            fig.for_each_trace(
                lambda trace: trace.update(
                    marker=dict(size=16 if trace.name == "Selected sample" else 8)
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            explained = pca.explained_variance_ratio_
            st.caption(
                f"Explained variance: PC1 = {explained[0]*100:.1f}%, "
                f"PC2 = {explained[1]*100:.1f}%"
            )

            target_row = pca_df[pca_df["sample"] == target_sample].iloc[0]

            pca_df["distance_to_target"] = pca_df.apply(
                lambda row: sqrt(
                    (row["PC1"] - target_row["PC1"])**2 +
                    (row["PC2"] - target_row["PC2"])**2
                ),
                axis=1
            )

            nearest_df = (
                pca_df[pca_df["sample"] != target_sample]
                .sort_values("distance_to_target")
                .head(5)[["sample", "PC1", "PC2", "distance_to_target"]]
            )

            st.markdown("### Nearest samples in PCA space")
            st.dataframe(nearest_df, use_container_width=True)

            st.markdown("### Classification decision")

            predicted_class = st.selectbox(
                "Predicted class",
                [
                    "Pure algae",
                    "Algae + BSA",
                    "Algae + Glucose",
                    "Mixture",
                    "Uncertain"
                ]
            )

            confidence = st.selectbox(
                "Confidence",
                ["Low", "Medium", "High"]
            )

            reasoning = st.text_area(
                "Reasoning",
                placeholder="Explain your classification using the PCA position and spectral evidence."
            )

            if st.button("Submit classification"):
                row = {
                    "time": datetime.now(),
                    "group": group_id,
                    "dataset": dataset_name,
                    "page": "Classify",
                    "target_sample": target_sample,
                    "predicted_class": predicted_class,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "pc1": float(target_row["PC1"]),
                    "pc2": float(target_row["PC2"])
                }

                pd.DataFrame([row]).to_csv(
                    "responses.csv",
                    mode="a",
                    header=not pd.io.common.file_exists("responses.csv"),
                    index=False
                )

                st.success("Classification saved.")

# =======================
# DASHBOARD
# =======================
elif page == "Dashboard":
    st.header("Instructor Dashboard")

    try:
        df_resp = pd.read_csv("responses.csv")
        st.dataframe(df_resp, use_container_width=True)
    except:
        st.info("No responses yet.")
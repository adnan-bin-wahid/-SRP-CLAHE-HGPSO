# Literature Map and Source Verification

Checked on 13 October 2026. This is a targeted literature investigation to position the implemented study, **not a systematic review** or proof that no similar method exists. Source identifiers L01-L19 are working keys for the research brief; the manuscript must use numbered IEEE citations in order of appearance.

Search themes included the exact supplied HGPSO title; CLAHE and adaptive gamma enhancement; PSO/GWO; hue-preserving common scaling and clipping; multispectral/low-light remote-sensing enhancement in 2024-2026; dataset documentation; NDVI/NDWI/SAM/SSIM; paired tests and spatially dependent evaluation. Preference was given to original papers, author-hosted manuscripts, institutional records, dataset providers, and official software/IEEE documentation. Some publisher pages were unavailable; the access/verification limits below are intentional.

## L01. HGPSO Source

**Citation candidate:** S. Rentapalli and A. K. Md Khairuzzaman, "Enhancement of Satellite Images Using Contrast-Limited Adaptive Histogram Equalization With Hybrid Grey Wolf and Particle Swarm Optimization," *IEEE Access*, vol. 14, pp. 5288-5316, 2026, doi: 10.1109/ACCESS.2026.3651193.

**Sources:** [DOI](https://doi.org/10.1109/ACCESS.2026.3651193); [author manuscript and bibliographic record](https://www.researchgate.net/publication/399470226_Enhancement_of_Satellite_Images_Using_Contrast-Limited_Adaptive_Histogram_Equalization_with_Hybrid_Grey_Wolf_and_Particle_Swarm_Optimization).

**Verified scope:** Accessible accepted-manuscript text identifies the authors and correct DOI in its acceptance footer. Publisher-deposited [Crossref metadata](https://api.crossref.org/works/10.1109%2FACCESS.2026.3651193) was subsequently checked and confirms authors, volume 14, pages 5288-5316, and year 2026. Some manuscript header fields retain template placeholders; do not infer publication year from them. The final formatted publisher PDF was not inspected.

**Use:** Introduction, Related Work, inherited transform/hybrid-search attribution, and HGPSO baseline disclosure. The source combines CLAHE with PSO/GWO and describes an eight-metric fitness formulation. This repository uses a separately specified five-term score and four-band adaptation. Source performance numbers are not this study's measurements and must not be inserted into the experimental table.

## L02. Adaptive Histogram Equalization and CLAHE

**Citation candidate:** S. M. Pizer *et al.*, "Adaptive histogram equalization and its variations," *Computer Vision, Graphics, and Image Processing*, vol. 39, no. 3, pp. 355-368, 1987, doi: 10.1016/S0734-189X(87)80186-X.

**Sources:** [institutional bibliographic record](https://research.tue.nl/en/publications/adaptive-histogram-equalization-and-its-variations/); [institution-hosted original paper](https://pure.tue.nl/ws/files/3234660/Metis225292.pdf).

**Use:** Historical foundation for adaptive/local histogram enhancement, not a citation for this repository's exact tile/interpolation behavior. Pair with the actual scikit-image API [L18] for implementation details.

**Optional original CLAHE chapter:** K. Zuiderveld, "Contrast limited adaptive histogram equalization," in *Graphics Gems IV*, 1994, pp. 474-485, doi: [10.1016/B978-0-12-336156-1.50061-6](https://doi.org/10.1016/B978-0-12-336156-1.50061-6). Bibliographic metadata identified; chapter text not reviewed in this audit. Verify the chapter record before adding the final entry.

## L03. AGCWD

**Citation candidate:** S.-C. Huang, F.-C. Cheng, and Y.-S. Chiu, "Efficient Contrast Enhancement Using Adaptive Gamma Correction With Weighting Distribution," *IEEE Transactions on Image Processing*, vol. 22, no. 3, pp. 1032-1041, 2013, doi: 10.1109/TIP.2012.2226047.

**Sources:** [original paper PDF](https://dept-info.labri.fr/~achille/ti/Activites/Note-de-lecture/Articles/efficient_contrast_enhancement_method_using_adaptative_gamma_correction_with_weighting_distribution_2013.pdf); [publication abstract](https://pubmed.ncbi.nlm.nih.gov/23144035/).

**Use:** Explain adaptive gamma based on a weighted intensity distribution. State that `agcwd_value` is an independent baseline implementation on HSV value, not the authors' released implementation or a validated four-band AGCWD reference.

## L04. Particle Swarm Optimization

**Original citation candidate:** J. Kennedy and R. Eberhart, "Particle swarm optimization," in *Proceedings of ICNN'95 - International Conference on Neural Networks*, vol. 4, 1995, pp. 1942-1948, doi: [10.1109/ICNN.1995.488968](https://doi.org/10.1109/ICNN.1995.488968). Original proceedings metadata identified; original full text not reviewed here.

**Accessible primary synthesis:** R. Poli, J. Kennedy, and T. Blackwell, "Particle swarm optimization," *Swarm Intelligence*, vol. 1, pp. 33-57, 2007, doi: [10.1007/s11721-007-0002-0](https://link.springer.com/article/10.1007/s11721-007-0002-0).

**Use:** Attribute swarm search and distinguish the general algorithm from the implemented inertia, acceleration constants, boundaries, evaluation protocol, and inherited hybrid. Avoid untested claims that PSO always explores better or is inherently slower.

## L05. Grey Wolf Optimizer

**Citation candidate:** S. Mirjalili, S. M. Mirjalili, and A. Lewis, "Grey Wolf Optimizer," *Advances in Engineering Software*, vol. 69, pp. 46-61, 2014, doi: 10.1016/j.advengsoft.2013.12.007.

**Sources:** [publisher article](https://www.sciencedirect.com/science/article/pii/S0965997813001853); [author/institution-hosted paper](https://research-repository.griffith.edu.au/bitstreams/a5b4826e-f238-4257-86b1-bf10fe1d3e1b/download).

**Use:** Cite leader-based parameter updates. The current hybrid implementation and feasibility ranking require a separate code-grounded description; this citation alone does not establish their correctness or novelty.

## L06. Common Scaling and Hue Preservation

**Citation candidate:** S. K. Naik and C. A. Murthy, "Hue-Preserving Color Image Enhancement Without Gamut Problem," *IEEE Transactions on Image Processing*, vol. 12, no. 12, pp. 1591-1598, 2003, doi: 10.1109/TIP.2003.819231.

**Source:** [author/institution-hosted original paper](https://www.isical.ac.in/~sarif_r/papers/naik12tip12_hue_preserving.pdf).

**Use:** Prior art for common-channel scaling, color consistency, and the need to handle gamut bounds. This prevents claiming that multiplying all channels by one scalar is itself a new invention. Extending the argument to the current RGB-NIR constraints is this study's mathematical explanation, not evidence that the source tested Sentinel-2 NDVI/NDWI.

## L07. Dataset and Acquisition Context

**Dataset citation candidate:** Radiant Earth Foundation, *Sentinel-2 Cloud Cover Segmentation Dataset*, version 1, 2022, doi: [10.34911/rdnt.hfq6m7](https://doi.org/10.34911/rdnt.hfq6m7).

**Sources:** [dataset provider repository](https://source.coop/radiantearth/cloud-cover-detection-challenge); [provider documentation](https://radiantearth.blob.core.windows.net/mlhub/ref_cloud_cover_detection_challenge_v1/documentation.pdf); [challenge organizer's data context](https://www.drivendata.org/competitions/83/cloud-cover/page/397/).

**Verified scope:** The distributed dataset contains 22,728 chips and is documented as CC BY 4.0. Challenge data are Sentinel-2 L2A imagery with expert cloud annotations and diverse locations. The **240 selected chips** and this project's validation/test partition are local study choices, not the full dataset or original challenge partition.

**Use:** Experimental Setup, attribution, availability, and limitations. Do not call this an enhancement ground-truth dataset or claim the method removes clouds.

## L08. NDVI Foundation

**Citation candidate:** J. W. Rouse, Jr., R. H. Haas, J. A. Schell, and D. W. Deering, "Monitoring vegetation systems in the Great Plains with ERTS," in *Third Earth Resources Technology Satellite-1 Symposium*, vol. 1, section A, NASA SP-351, 1974, pp. 309-317.

**Sources:** [NASA record](https://ntrs.nasa.gov/citations/19740022614); [NASA-hosted paper](https://ntrs.nasa.gov/api/citations/19740022614/downloads/19740022614.pdf).

**Use:** NDVI's red/NIR normalized difference. The symposium occurred in 1973 and the proceedings publication is 1974; do not confuse these dates. The NASA record identifier is not an invented DOI. NDVI agreement with the input is not proof of vegetation-map accuracy.

## L09. Green-NIR NDWI

**Citation candidate:** S. K. McFeeters, "The use of the Normalized Difference Water Index (NDWI) in the delineation of open water features," *International Journal of Remote Sensing*, vol. 17, no. 7, pp. 1425-1432, 1996, doi: 10.1080/01431169608948714.

**Source:** [original publisher record](https://www.tandfonline.com/doi/abs/10.1080/01431169608948714).

**Verification limit:** Publisher-deposited [Crossref metadata](https://api.crossref.org/works/10.1080%2F01431169608948714) confirms the author, title, year, volume, issue, and pages. The publisher body was unavailable. The green-NIR formula in this study was verified directly in code; obtain the original paper before making more detailed source-specific interpretations.

**Use:** Explicitly name the McFeeters green/NIR index. Do not cite a SWIR-based NDWI definition for a four-band cube without SWIR. Input agreement does not establish improved water detection.

## L10. Spectral Angle Mapper

**Citation candidate:** F. A. Kruse *et al.*, "The Spectral Image Processing System (SIPS) - Interactive visualization and analysis of imaging spectrometer data," *Remote Sensing of Environment*, vol. 44, nos. 2-3, pp. 145-163, 1993, doi: 10.1016/0034-4257(93)90013-N.

**Sources:** [original publisher article](https://www.sciencedirect.com/science/article/pii/003442579390013N); [official ENVI SAM documentation](https://www.nv5geospatialsoftware.com/docs/spectralanglemapper.html).

**Use:** Explain angular spectral similarity and scale insensitivity. This study measures input-output angle in **degrees**; the documentation's classification thresholds use radians. It does not perform endmember classification or prove recovered reflectance magnitude.

## L11. SSIM and Reference Interpretation

**Citation candidate:** Z. Wang, A. C. Bovik, H. R. Sheikh, and E. P. Simoncelli, "Image Quality Assessment: From Error Visibility to Structural Similarity," *IEEE Transactions on Image Processing*, vol. 13, no. 4, pp. 600-612, 2004, doi: 10.1109/TIP.2003.819861.

**Sources:** [author-hosted paper](https://ece.uwaterloo.ca/~z70wang/publications/ssim.pdf); [author's SSIM page](https://ece.uwaterloo.ca/~z70wang/research/ssim/).

**Use:** Interpret SSIM as similarity relative to a specified reference. In the main experiment the reference is the input, so call it input fidelity, not clean-reference enhancement quality. In the synthetic experiment it is the undegraded observed chip. Exact scikit-image settings differ from the original paper's canonical configuration [L18].

## L12. Holm Multiple-Comparison Correction

**Citation candidate:** S. Holm, "A Simple Sequentially Rejective Multiple Test Procedure," *Scandinavian Journal of Statistics*, vol. 6, no. 2, pp. 65-70, 1979.

**Sources:** [journal article record](https://www.jstor.org/stable/4615733); [original article PDF](https://www.ime.usp.br/~abe/lista/pdf4R8xPVzCnX.pdf).

**Use:** Attribute sequential family-wise correction. This study defines a family of seven comparisons **per metric**, not one family spanning all metric-comparison combinations. State this clearly. Report adjusted p-values, paired units, and effect sizes; correction does not solve correlated sampling or validate metric choice.

## L13. Recent Learned Multispectral Enhancement

**Citation candidate:** S. Suresh, R. Rajan M., C. S. Asha, and F. Dell'Acqua, "RDC-UNet++: An end-to-end network for multispectral satellite image enhancement," *Remote Sensing Applications: Society and Environment*, vol. 36, article 101293, 2024, doi: 10.1016/j.rsase.2024.101293.

**Sources:** [publisher article](https://www.sciencedirect.com/science/article/pii/S2352938524001575); [author institution's publication record](https://researcher.manipal.edu/en/publications/rdc-unet-an-end-to-end-network-for-multispectral-satellite-image-/).

**Verified scope:** Publisher abstract and indexed institutional metadata identify an end-to-end residual/dense U-Net++ approach. Full comparative tables and author-name formatting were not completely verified; confirm the publisher citation export before building the final bibliography.

**Use:** Establish that learned multispectral enhancement is relevant contemporary context. It was not run in this study. Do not claim superior visual quality, spectral accuracy, or cost relative to it.

## L14. Recent Learned Low-Light Remote-Sensing Enhancement

**Authors/title:** Z. Yao, G. Fan, J. Fan, M. Gan, and C. L. P. Chen, "Spatial-frequency Dual-Domain Feature Fusion Network for Low-Light Remote Sensing Image Enhancement," 2024.

**Sources:** [author preprint, arXiv:2404.17400v2](https://arxiv.org/abs/2404.17400v2); [related journal DOI linked by the author record](https://doi.org/10.1109/TGRS.2024.3434416).

**Verified scope:** Author abstract describes amplitude/phase processing, dual-domain feature fusion, and two low-light remote-sensing datasets. The author record links a journal DOI; journal volume/article number was not verified here. Cite the verified preprint or retrieve the complete journal record, rather than inventing missing fields.

**Use:** Related Work and the need for genuine low-light evaluation. There is no experiment comparing this trained model with the current method, and its dataset is not interchangeable with the selected cloud-cover chips.

## L15. Recent Hue-Preserving Contrast Enhancement

**Citation candidate:** Y. Ueda and N. Suetake, "CCC-Trans: Hue-preserving color image enhancement method based on convex combination coefficient transformation," *Franklin Open*, vol. 10, article 100213, 2025, doi: 10.1016/j.fraope.2025.100213.

**Sources:** [publisher article](https://www.sciencedirect.com/science/article/pii/S2773186325000039); [author-maintained publication record](https://researchmap.jp/yoshiaki_ueda/published_papers/48901423).

**Verified scope:** Indexed publisher text and author record identify an RGB hue-preserving/gamut-conscious method. Publisher-deposited [Crossref metadata](https://api.crossref.org/works/10.1016%2Fj.fraope.2025.100213) confirms both authors, 2025, volume 10, and article 100213. The publisher page body was not retrievable directly.

**Use:** Recent evidence that color-consistent enhancement and gamut handling remain active topics. Do not misdescribe it as an RGB-NIR spectral-preservation experiment or an evaluated baseline.

## L16. Spatial Dependence and Validation

**Citation candidate:** D. R. Roberts *et al.*, "Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure," *Ecography*, vol. 40, no. 8, pp. 913-929, 2017, doi: 10.1111/ecog.02881.

**Source:** [original publisher paper](https://nsojournals.onlinelibrary.wiley.com/doi/10.1111/ecog.02881).

**Use:** Motivate location/acquisition grouping and caution about structured dependence. This study's 50-group analysis is a retrospective sensitivity check, not an implementation of geographically verified blocked cross-validation or proof of independent sampling.

## L17. Statistical Implementation Documentation

**Sources:** [SciPy Wilcoxon](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html); [SciPy Friedman](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.friedmanchisquare.html).

**Use:** Specify two-sided tests, `zero_method='wilcox'`, `method='auto'`, and ties/zeros handling. The run used its recorded SciPy version; current online documentation may differ. Inspect saved configuration/environment before claiming reproducibility across versions. Friedman is an omnibus comparison, not a substitute for the selected paired contrasts or dependence checks.

**Citation role:** Official documentation can accompany reproducibility details; it does not replace original statistical references if the target venue expects them.

## L18. Image-Processing Implementation Documentation

**Sources:** [scikit-image exposure/CLAHE](https://scikit-image.org/docs/stable/api/skimage.exposure.html); [scikit-image SSIM](https://scikit-image.org/docs/stable/api/skimage.metrics.html).

**Use:** Document normalized CLAHE clip limit and actual SSIM settings. This implementation obtains a full SSIM map with `data_range=1` and averages valid pixels; defaults include a uniform 7 x 7 window and sample covariance. It does not exactly match the canonical Gaussian-window SSIM configuration. Local neighborhoods can include filled invalid pixels. Cite actual recorded library versions separately.

## L19. IEEE Formatting and Venue Selection

**Sources:** [IEEE authoring tools and templates](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/); [official template selector](https://template-selector.ieee.org/).

**Use:** Select the actual venue's template rather than modifying margins/fonts to force length. The current IEEEtran journal-mode scaffold is provisional. Two-column layout is not double-sided printing, and ten pages is the user's project limit, not a universal IEEE limit. Final length is measured from the compiled PDF, including references and floats.

## Additional Candidates, Not Yet Required Citations

A 2026 dehazing article, *Remote Sensing Image Dehazing via Fusing Brightness Decomposition and Saturation Adjustment*, doi: [10.1109/TGRS.2026.3659866](https://ieeexplore.ieee.org/document/11370272/), was located through its publisher-indexed abstract. Full author metadata/content remain unchecked, and dehazing is a distinct problem. It should not be used to imply a new comparison or padded into the bibliography.

Pansharpening literature was also considered because multiplicative spectral scaling appears in fusion methods. This experiment has no panchromatic input, resampling-based resolution increase, or fusion evaluation; therefore do not frame its results as pansharpening or super-resolution.

## Synthesis for the Writing Decision

- Reuse/adaptation must be credited: CLAHE, the local transform and hybrid foundation, swarm algorithms, indices, SAM, and reference-based metrics.
- Shared scaling is not independently novel. The proposed contribution must rely on the four-band constrained implementation and transparent empirical evaluation.
- Common-gain CLAHE is the essential control: it already offers low spectral errors without search. The statistically established added benefit here is contrast, with substantial additional cost and lower input fidelity.
- Contemporary learned enhancement and gamut-conscious methods should be acknowledged, but this study cannot claim to outperform them without running appropriate comparable experiments.
- Sources and citations support context/definitions. **Every new experimental numerical claim must come from the local saved evidence**, not a source paper's reported results.

Before submission, verify every final bibliography entry against a publisher/author record, resolve the metadata-only flags, check links, and ensure every entry is cited. Do not convert this preparation list wholesale into an uncited reference list.

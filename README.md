# CyberShake Data Selection and Aquisition

***UPDATES TO THE USC SERVERS:***
***CODE CURRENTLY NOT WORKING AS INTENDED***

The selection and acquisition of CyberShake simulations and metadata can be separated into four parts: (1) event selection, (2) metadata acquisition, (3) waveform acquisition, and (4) data compilation. The procedure outline below can be followed using the tools made available at github.com/scndn/cybershake and necessitates a basic knowledge of programming and access to the intensity@usc.edu server.

In (1) event selection, we query the CyberShake SQL database for all simulated ground motions belonging to Study 15.4 and return a subset of unique simulation identification integers (IDs).

In (2) metadata acquisition, we use the subset of simulation IDs from step (1) to query the CyberShake SQL database for all relevant metadata related to the earthquake source and recording station. This information includes source magnitude, source hypocenter, station location, Vs30, Z1.0, and Z2.5.

In (3) waveform acquisition, we use the subset of simulation IDs from step (1) to download simulated waveforms and earthquake source rupture files stored on intensity@usc.edu. Each earthquake source rupture file contains a grid of point sources defined by latitude, longitude, depth, rake, dip, and strike.

In (4) data compilation, we compile existing and compute additional metadata using the earthquake source rupture files and process the simulated waveforms using scripts made available on intensity@usc.edu. We compute Rrup using the site location and earthquake rupture discretization, Ztor using the earthquake source rupture file, and rake angle as the weighted average rake of the rupture discretization.

The final database of selected CyberShake v15.4 acceleration time histories and metadata include the following metadata for each simulated ground motion: Run_ID, Source_ID, Rupture_ID, Rupture_Variation_ID, earthquake source name, earthquake magnitude, Site_ID, site name, Rrup, Vs30, Ztor, Z1.0, Z2.5, rake, and accompanying acceleration time histories.


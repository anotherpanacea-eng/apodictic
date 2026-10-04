### SETEC renderer delivery guidance

Correct the Pass 3/Pass 7 design record's unsupported stdout-delivery instruction
for heatmap and voice-drift renderers. Their direct scripts use JSON sidecars;
future normalized file delivery still requires separate producer qualification,
an actual integrated release floor and scripted consumer sync. Reconcile the
current v1.132.0 pin while retaining the July snapshot as historical evidence.
No renderer admission, consumer pin or runtime behavior changes.

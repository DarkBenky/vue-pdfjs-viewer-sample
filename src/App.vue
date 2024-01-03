<template>
  <h1>i am asking my self</h1>
  <canvas id="theCanvas"></canvas>
</template>

<script>
import * as pdfjsLib from "pdfjs-dist";
import "pdfjs-dist/build/pdf.worker.mjs";

export default {
  name: 'App',
  components: {},
  methods: {
    async file_load() {
      const pdfPath = "dummy.pdf";

      // Setting worker path to worker bundle.
      pdfjsLib.GlobalWorkerOptions.workerSrc = "/node_modules/pdfjs-dist/build/pdf.worker.mjs";

      // Loading a document.
      const loadingTask = pdfjsLib.getDocument(pdfPath);
      const pdfDocument = await loadingTask.promise;

      // Request a first page
      const pdfPage = await pdfDocument.getPage(1);

      // Display page on the existing canvas with 100% scale.
      const viewport = pdfPage.getViewport({ scale: 1.0 });
      const canvas = document.getElementById("theCanvas");
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      const ctx = canvas.getContext("2d");

      // Render PDF content
      const renderTask = pdfPage.render({
        canvasContext: ctx,
        viewport,
      });
      await renderTask.promise;

      // Add an image to the canvas after the PDF rendering is complete
      const img = new Image();
      img.src = "logo.png"; // Replace with the path to your image
      await new Promise((resolve) => {
        img.onload = resolve;
      });

      // Draw the image on the canvas
      ctx.drawImage(img, 100, 100, 100, 100);
    },
  },
  mounted() {
    this.file_load();
  },
};
</script>

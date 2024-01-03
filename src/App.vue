<template>
  <div>
    <h1>i am asking my self</h1>
    <input type="file" @change="handleImageUpload" accept="image/*" />
    <canvas id="theCanvas" @click="handleCanvasClick" @mousemove="handleMouseMove" @mouseup="handleMouseUp"></canvas>
    <!-- TODO : fix rendering of images -->
    <button @click="file_load">render images</button>
  </div>
</template>

<script>
import * as pdfjsLib from "pdfjs-dist";
import "pdfjs-dist/build/pdf.worker.mjs";

export default {
  name: 'App',
  components: {},
  data() {
    return {
      pdfPath: "dummy.pdf",
      images: [
      ],
      activeImageIndex: 0,
      offsetX: 0,
      offsetY: 0,
      isDragging: false,
    };
  },
  methods: {
    async file_load() {
      const pdfPath = this.pdfPath;

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

      // Draw all images on the canvas
      this.images.forEach((image) => {
        if (image.src) {
          const img = new Image();
          img.src = image.src;
          console.log(image.src + " " + image.x + " " + image.y);
          ctx.drawImage(img, image.x, image.y, image.size_x, image.size_y);
        }
      });
    },
    handleImageUpload(event) {
      console.log("adding image ");
      const file = event.target.files[0];
      if (file) {
        // const imageSrc = URL.createObjectURL(file);
        this.images.push({ src: "logo.png", x: 0, y: 0, clicked: false , size_x: 100, size_y: 100});
        // Reset the file input to allow uploading the same file again
        event.target.value = null;
        // Trigger a redraw of the canvas to reflect the new image
        // this.file_load();
      }
    },
    handleCanvasClick(event) {
      const canvas = event.target;
      const rect = canvas.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      // Check if an image is clicked
      this.images.forEach((image, index) => {
        const imgX = image.x;
        const imgY = image.y;
        // const imgWidth = 100;
        // const imgHeight = 100;

        console.log(image);

        if (image.clicked == false) {
          console.log("clicked on image " + index);
          this.images[index].clicked = true;
          this.activeImageIndex = index;

          // Calculate offset to maintain relative position while dragging
          this.offsetX = x - imgX;
          this.offsetY = y - imgY;

          this.isDragging = true;
          image.clicked = true;
        }
      });
      console.log(this.images);
    },
    handleMouseMove(event) {
      if (this.isDragging) {
        const canvas = event.target;
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        // Update the position of the active image
        this.images[this.activeImageIndex].x = x - this.offsetX;
        this.images[this.activeImageIndex].y = y - this.offsetY;

        // Redraw the canvas
        // this.file_load();
      }
    },
    handleMouseUp() {
      this.isDragging = false;
    },
  },
  mounted() {
    this.file_load();
  },
};
</script>

<style>
body {
  background-color: black;
}
</style>

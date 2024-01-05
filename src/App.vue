<template>
	<div>
		<h1>i am asking my self</h1>
		<input type="file" @change="handleImageUpload" accept="image/*" />
		<canvas
			id="theCanvas"
			@click="handleCanvasClick"
			@mousemove="handleMouseMove"
			@mouseup="handleMouseUp"
			@mousedown="handleMouseDown"
		></canvas>
		<div v-for="(overlay, index) in this.overlays" :key="index">
			<!-- TODO add rendering of multiple overlays -->
      <div :style="{ left: overlay.left, top: overlay.top, width: overlay.width, height: overlay.height, position: 'absolute', backgroundColor: 'red', opacity: '0.3' }"></div>
		</div>
    <button @click="addOverlay">add overlay</button>
		<div id="redOverlay" ref="redOverlay"></div>
		<!-- TODO : fix rendering of images -->
		<button @click="file_load">render images</button>
	</div>
</template>

<script>
import * as pdfjsLib from "pdfjs-dist";
import "pdfjs-dist/build/pdf.worker.mjs";

export default {
	name: "App",
	components: {},
	data() {
		return {
			pdfPath: "dummy.pdf",
			images: [],
			overlays: [],
			activeImageIndex: 0,
			offsetX: 0,
			offsetY: 0,
      isDragging: false,
      overlay: false,
      left: 0,
      top: 0,
      width: 0,
      height: 0,
		};
	},
	methods: {
		async file_load() {
			const pdfPath = this.pdfPath;

			// Setting worker path to worker bundle.
			pdfjsLib.GlobalWorkerOptions.workerSrc =
				"/node_modules/pdfjs-dist/build/pdf.worker.mjs";

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
					ctx.drawImage(
						img,
						image.x,
						image.y,
						image.size_x,
						image.size_y
					);
				}
			});
    },
    addOverlay(){
      this.overlay = true
      console.log(this.overlay)
    },
		handleImageUpload(event) {
			console.log("adding image ");
			const file = event.target.files[0];
			if (file) {
				// const imageSrc = URL.createObjectURL(file);
				this.images.push({
					src: "logo.png",
					x: 0,
					y: 0,
					clicked: false,
					size_x: 100,
					size_y: 100,
				});
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

			// Draw a red div overlay
			const redOverlay = this.$refs.redOverlay;
			redOverlay.style.position = "absolute";
			redOverlay.style.backgroundColor = "red";
			redOverlay.style.opacity = "0.3";

			// Check if an image is clicked
			this.images.forEach((image, index) => {
				console.log(image);
				if (image.clicked == false) {
					console.log("clicked on image " + index);
					this.images[index].clicked = true;
					this.activeImageIndex = index;

					this.images[index].x = x;
					this.images[index].y = y;

					image.clicked = true;
				}
			});
			console.log(this.images);
			// TODO : why we need to call this twice ???
			// this.file_load();
			// this.file_load();
		},
    handleMouseMove(event) {
			if (this.isDragging && this.overlay) {
				// const canvas = event.target;
				// const rect = canvas.getBoundingClientRect();

				// Update the position of the red div overlay
				const redOverlay = this.$refs.redOverlay;

				// Use canvas coordinates for both starting and ending positions
				const startX = this.dragStartX;
				const startY = this.dragStartY;
				// console.log(startX, startY, 'dragStartX', 'dragStartY',);
				const endX = event.clientX;
				const endY = event.clientY;

				const minX = Math.min(startX, endX);
				const minY = Math.min(startY, endY);
				const width = Math.abs(endX - startX);
				const height = Math.abs(endY - startY);

				redOverlay.style.left = `${minX}px`;
				redOverlay.style.top = `${minY}px`;
				redOverlay.style.width = `${width}px`;
        redOverlay.style.height = `${height}px`;

        this.left = `${minX}px`;
        this.top = `${minY}px`;
        this.width = `${width}px`;
        this.height = `${height}px`;
			}
		},
		handleMouseDown(event) {
			// const canvas = event.target;
			// const rect = canvas.getBoundingClientRect();
			this.dragStartX = event.clientX;
			this.dragStartY = event.clientY;
      this.isDragging = true;
		},
    handleMouseUp() {
      if (this.overlay) {
        this.isDragging = false;
        this.overlay = false;
        this.overlays.push({ "left": this.left, "top": this.top, "width": this.width, "height": this.height });
        console.log(this.overlays); 
      }
		},
	},
	mounted() {
		this.file_load();
	},
};
</script>

<style>
body {
	background-color: rgb(94, 94, 94);
}
</style>

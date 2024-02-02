<template>
	<div>
		<h1>i am asking my self</h1>
		<canvas id="theCanvas" @click="handleCanvasClick" @mousemove="handleMouseMove" @mouseup="handleMouseUp"
			@mousedown="handleMouseDown"></canvas>
		<div v-for="(overlay, index) in this.overlays" :key="index">
			<div :style="{
				left: overlay.left,
				top: overlay.top,
				width: overlay.width,
				height: overlay.height,
				position: 'absolute',
				backgroundImage: 'url(' + overlay.img + ')',
				backgroundSize: 'cover',
				opacity: '0.3'
			}"></div>
		</div>
		<div v-for="(overlay, index) in this.overlays" :key="index">
			<div :style="{
				backgroundImage: 'url(' + overlay.img + ')',
				width: '200px',
				height: '200px',
			}">
			<button @click="delete_image(index)">delete</button>
		</div>
		</div>
		<button @click="addOverlay">add overlay</button>
		<div id="redOverlay" ref="redOverlay"></div>
		<input type="file" ref="fileInput" accept="image/*" @change="handleFileChange" />
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
			currentImage: NaN,
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
		addOverlay() {
			this.overlay = true
			console.log(this.overlay)
		},

		delete_image(index) {
			this.overlays.splice(index, 1);
		},

		handleFileChange(event) {
			// Handle the file change event here
			const selectedFile = event.target.files[0];

			// Check if a file is selected
			if (selectedFile) {
				// Read the file as a data URL
				const reader = new FileReader();
				reader.onload = () => {
					// Add the data URL to the images array
					this.currentImage = reader.result;
				};

				reader.readAsDataURL(selectedFile);
			}
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

				redOverlay.style.position = "absolute";
				redOverlay.style.left = `${minX}px`;
				redOverlay.style.top = `${minY}px`;
				redOverlay.style.width = `${width}px`;
				redOverlay.style.height = `${height}px`;
				redOverlay.style.backgroundImage = 'url(' + this.currentImage + ')';
				redOverlay.style.backgroundSize = 'cover';
				redOverlay.style.opacity = "0.3";


				this.left = `${minX}px`;
				this.top = `${minY}px`;
				this.width = `${width}px`;
				this.height = `${height}px`;
				this.img = this.currentImage;
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
				this.overlays.push({ "left": this.left, "top": this.top, "width": this.width, "height": this.height, img: this.currentImage });
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
	background-color: rgb(66, 66, 66);
}
</style>

<template>
	<div>
		<h1>i am asking my self</h1>
		<canvas id="theCanvas" @click="handleCanvasClick" @mousemove="handleMouseMove" @mouseup="handleMouseUp"
			@mousedown="handleMouseDown"></canvas>
		<button @click="addOverlay">add overlay</button>
		<div id="redOverlay" ref="redOverlay"></div>
		<input type="file" ref="fileInput" accept="image/*" @change="handleFileChange" />
	</div>
	<div v-for="(overlay, index) in this.overlays" :key="index">
			<div :style="{
				left: overlay.left,
				top: overlay.top,
				width: overlay.width,
				height: overlay.height,
				position: 'absolute',
				backgroundImage: 'url(' + overlay.low_res_img + ')',
				backgroundSize: 'contain',
				backgroundRepeat: 'no-repeat',
				backgroundPosition: 'center',
				opacity: '0.3',
				pointerEvents: 'none'
			}"></div>
	</div>
	<div v-for="(overlay, index) in this.overlays" :key="index">
			<div :style="{
				backgroundImage: 'url(' + overlay.low_res_img + ')',
				backgroundSize: 'contain',
				height: '100px',
				width: '100px'
			}">
				<button @click="delete_image(index)">delete</button>
			</div>
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
			low_res_img: NaN,
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
					// Create an Image element for downsizing
					const img = new Image();
					img.src = reader.result;

					img.onload = () => {
						// Set the original image data URL
						this.currentImage = reader.result;

						// Set the new width and height for downscaling
						const newWidth = 250;
						const newHeight = (img.height / img.width) * newWidth;

						// Create a canvas element to draw the downscaled image
						const canvas = document.createElement('canvas');
						const ctx = canvas.getContext('2d');

						canvas.width = newWidth;
						canvas.height = newHeight;

						// Draw the image on the canvas with the new size
						ctx.drawImage(img, 0, 0, newWidth, newHeight);

						// Save the downscaled image as a data URL
						const downscaledImage = canvas.toDataURL();

						// Add the downscaled image data URL to the low_res_img array
						this.low_res_img = downscaledImage;
					};
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
				redOverlay.style.backgroundImage = 'url(' + this.low_res_img + ')';
				redOverlay.style.backgroundSize = 'contain';
				redOverlay.style.backgroundRepeat = 'no-repeat';
				redOverlay.style.backgroundPosition = 'center';
				redOverlay.style.opacity = "0.3";
				redOverlay.style.pointerEvents = 'none';


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
				this.overlays.push({ "left": this.left, "top": this.top, "width": this.width, "height": this.height, img: this.currentImage , "low_res_img": this.low_res_img });
				console.log(this.overlays);
				const redOverlay = this.$refs.redOverlay;
				redOverlay.style.opacity = "0";
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

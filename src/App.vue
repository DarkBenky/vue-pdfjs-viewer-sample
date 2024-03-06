<!-- TODO: get number of pages and be able to move there -->
<template>
	<div>
		<div>
			<button @click="handlePrevious">Previous</button>
			<button @click="handleNext">Next</button>
			<p>{{ page_number }} / {{ numberOfPages }} page</p>

			<input id="pageNumber-input" type="number" />
			<button @click="handlePageChange">Go to page</button>
		</div>
		<button @click="exportData">export</button>
	</div>
	<div @mousemove="handleDragging" @mousedown="handleDraggingStop">
		<h1>i am asking my self</h1>
		<canvas id="theCanvas" @click="handleCanvasClick" @mousemove="handleMouseMove" @mouseup="handleMouseUp"
			@mousedown="handleMouseDown"></canvas>
		<button @click="addOverlay">add overlay</button>
		<div id="redOverlay" ref="redOverlay"></div>
		<div id="BgOverlay" ref="BgOverlay"></div>
		<input type="file" ref="fileInput" accept="image/*" @change="handleFileChange" />
	</div>
	<div v-for="(overlay, index) in this.overlays" :key="index">
		<div v-if="overlay.page_number === this.page_number" @mousedown="handleDragStart(index)" :style="{
			left: overlay.left,
			top: overlay.top,
			width: overlay.width,
			height: overlay.height,
			position: 'absolute',
			backgroundImage: 'url(' + overlay.low_res_img + ')',
			backgroundSize: 'contain',
			backgroundRepeat: 'no-repeat',
			backgroundPosition: 'center',
			opacity: '0.4',
			pointerEvents: overlay.pointerEvents,
			border: overlay.border_color,
		}">
		</div>
	</div>
	<div v-for="(overlay, index) in this.overlays" :key="index">
		<div v-if="overlay.page_number === this.page_number" :style="{
			backgroundImage: 'url(' + overlay.low_res_img + ')',
			backgroundSize: 'contain',
			backgroundRepeat: 'no-repeat',
			backgroundPosition: 'center',
			height: '100px',
			width: '100px'
		}">
			<button @click="handleEdit(index)">edit</button>
			<div v-if="currentEdit === index">
				<button @click="delete_image(index)">delete</button>
				<button @click="handleScaling(index, 0.75)">-</button>
				<button @click="handleScaling(index, 1.25)">+</button>
			</div>
		</div>
	</div>
</template>

<script>
import * as pdfjsLib from "pdfjs-dist";
import "pdfjs-dist/build/pdf.worker.mjs";
import { saveAs } from 'file-saver';

export default {
	name: "App",
	components: {},
	data() {
		return {
			pdfPath: "big-pdf.pdf",
			images: [],
			low_res_img: NaN,
			overlays: [],
			offsetX: 0,
			offsetY: 0,
			isDragging: false,
			overlay: false,
			left: 0,
			top: 0,
			width: 0,
			height: 0,
			currentImage: NaN,
			currentEdit: NaN,
			dragging: false,
			indexDraggedImg: NaN,
			page_number: 1,
			numberOfPages: NaN,
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

			// get number of pages
			this.numberOfPages = pdfDocument.numPages;

			// Request a first page
			const pdfPage = await pdfDocument.getPage(this.page_number);

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

			// // Draw all images on the canvas
			// this.images.forEach((image) => {
			// 	if (image.src) {
			// 		const img = new Image();
			// 		img.src = image.src;
			// 		console.log(image.src + " " + image.x + " " + image.y);
			// 		ctx.drawImage(
			// 			img,
			// 			image.x,
			// 			image.y,
			// 			image.size_x,
			// 			image.size_y
			// 		);
			// 	}
			// });
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
			if (this.isDragging && this.overlay && this.currentImage) {
				// const canvas = event.target;
				// const rect = canvas.getBoundingClientRect();

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

				const BgOverlay = this.$refs.BgOverlay;

				BgOverlay.style.position = "absolute";
				BgOverlay.style.left = `${minX}px`;
				BgOverlay.style.top = `${minY}px`;
				BgOverlay.style.width = `${width}px`;
				BgOverlay.style.height = `${height}px`;
				BgOverlay.style.backgroundColor = 'red';
				BgOverlay.style.opacity = "0.1";
				BgOverlay.style.pointerEvents = 'none';

				// Update the position of the red div overlay
				const redOverlay = this.$refs.redOverlay;

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
			console.log('handleMouseDown');
			// const canvas = event.target;
			// const rect = canvas.getBoundingClientRect();
			if (isNaN(this.currentImage) && this.overlay) {
				console.log('handleMouseDown - True');
				this.dragStartX = event.clientX;
				this.dragStartY = event.clientY;
				this.isDragging = true;
			}
		},
		handleMouseUp() {
			if (this.overlay && this.currentImage) {
				this.isDragging = false;
				this.overlay = false;
				this.overlays.push({
					"left": this.left,
					"top": this.top,
					"width": this.width,
					"height": this.height,
					img: this.currentImage,
					"low_res_img": this.low_res_img,
					'border_color': 'none',
					'pointerEvents': 'none',
					'page_number': this.page_number
				});
				console.log(this.overlays);
				const redOverlay = this.$refs.redOverlay;
				redOverlay.style.opacity = "0";
				const BgOverlay = this.$refs.BgOverlay;
				BgOverlay.style.opacity = "0";
			}
		},
		handleScaling(index, scale) {
			const x = this.overlays[index].width.split(' ').map(value => parseInt(value, 10));
			const y = this.overlays[index].height.split(' ').map(value => parseInt(value, 10));
			this.overlays[index].width = parseInt((x * scale) + 1) + 'px';
			this.overlays[index].height = parseInt((y * scale) + 1) + 'px';
			// console.log(this.overlays[index].width, this.overlays[index].height);
		},
		handleEdit(index) {
			this.currentEdit = index;
			// Reset border_color for all overlays
			this.overlays.forEach((overlay, i) => {
				overlay.border_color = i === index ? '2px solid red' : 'none';
				overlay.pointerEvents = i === index ? 'auto' : 'none';
			});
		},
		handleDragStart(index) {
			if (this.currentEdit === index) {
				this.dragging = !this.dragging;
				this.indexDraggedImg = index;
				console.log(this.indexDraggedImg);
				this.overlays[index].pointerEvents = 'none';
			}
		},
		handleDragging(event) {
			if (this.dragging) {
				// get mouse position
				let mouseX = event.clientX;
				let mouseY = event.clientY;

				// Schedule the update using requestAnimationFrame
				requestAnimationFrame(() => {
					// set new image position
					this.overlays[this.indexDraggedImg].left = `${mouseX + 5}px`;
					this.overlays[this.indexDraggedImg].top = `${mouseY + 5}px`;
				});
			}
		},
		handleDraggingStop() {
			console.log(this.dragging);
			console.log(this.indexDraggedImg);
			if (this.dragging && !isNaN(this.indexDraggedImg)) {
				this.dragging = false;
				this.overlays[this.indexDraggedImg].pointerEvents = 'auto';
				this.indexDraggedImg = NaN;
			}
		},

		async handleNext() {
			try {
				this.page_number++;
				await this.file_load();
			} catch (error) {
				console.log(error);
			}
		},

		async handlePrevious() {
			try {
				if (this.page_number > 1) {
					this.page_number--;
					await this.file_load();
				}
			} catch (error) {
				console.log(error);
			}

		},

		async fetchRawPdfData(pdfPath) {
			try {
				const response = await fetch(pdfPath);
				if (!response.ok) {
					throw new Error(`Failed to fetch PDF data: ${response.status} - ${response.statusText}`);
				}

				const rawData = await response.blob();
				console.log(rawData);

				// Convert Blob to data URL
				const dataUrl = await new Promise((resolve) => {
					const reader = new FileReader();
					reader.onloadend = () => resolve(reader.result);
					reader.readAsDataURL(rawData);
				});

				return dataUrl;
			} catch (error) {
				throw new Error(`Error fetching raw PDF data: ${error.message}`);
			}
		},

		exportData() {
			console.log('export_data');

			// Fetch the raw PDF data
			this.fetchRawPdfData(this.pdfPath)
				.then(rawDataUrl => {
					// Once the data is fetched, construct the data object
					let data_export = []
					for (let i = 0; i < this.overlays.length; i++) {
						let stripData = {
							'left': this.overlays[i].left,
							'top': this.overlays[i].top,
							'width': this.overlays[i].width,
							'height': this.overlays[i].height,
							'image': this.overlays[i].img,
							'pageNumber': this.overlays[i].page_number,

						}
						data_export.push(stripData)
					}
					let data = {
						'Overlays': data_export,
						'PdfFile': rawDataUrl,
					};

					console.log(data);
					// Save the data as a JSON file
					let blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
					saveAs(blob, 'sample.json');
				})
				.catch(error => {
					console.error('Error fetching raw PDF data:', error);
				});
		},
		async handlePageChange() {
			let pageNumber = document.getElementById('pageNumber-input').value;
			try {
				if (pageNumber > 0 && pageNumber <= this.numberOfPages) {
					this.page_number = parseInt(pageNumber);
					await this.file_load();
				}
			} catch (error) {
				console.log(error);
			}
		}
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

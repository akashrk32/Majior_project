package com.shilora.app.ui.screens.explore

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.material.icons.filled.Place
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.shilora.app.di.ServiceLocator
import com.shilora.app.domain.model.HeritageItem
import com.shilora.app.theme.*
import com.shilora.app.ui.components.PrimaryTopBar
import com.shilora.app.ui.components.ShiloraCard

@Composable
fun ExploreScreen(
    onItemClick: (String) -> Unit
) {
    val heritageRepository = remember { ServiceLocator.heritageRepository }
    val itemsFlow = remember { heritageRepository.getCuratedInscriptions() }
    val allItems by itemsFlow.collectAsState(initial = emptyList())

    var searchQuery by remember { mutableStateOf("") }
    var selectedCategory by remember { mutableStateOf("All") }

    val categories = listOf("All", "Hero Stones", "Land Grants", "Temple Dedications", "Kadamba", "Chalukya", "Hoysala")

    val filteredItems = remember(allItems, searchQuery, selectedCategory) {
        allItems.filter { item ->
            val matchesSearch = searchQuery.isBlank() ||
                item.title.contains(searchQuery, ignoreCase = true) ||
                item.region.contains(searchQuery, ignoreCase = true) ||
                item.dynasty.contains(searchQuery, ignoreCase = true)

            val matchesCategory = when (selectedCategory) {
                "All" -> true
                "Hero Stones" -> item.inscriptionType.contains("Hero", ignoreCase = true) || item.inscriptionType.contains("Memorial", ignoreCase = true)
                "Land Grants" -> item.inscriptionType.contains("Grant", ignoreCase = true)
                "Temple Dedications" -> item.inscriptionType.contains("Temple", ignoreCase = true)
                "Kadamba" -> item.dynasty.contains("Kadamba", ignoreCase = true)
                "Chalukya" -> item.dynasty.contains("Chalukya", ignoreCase = true)
                "Hoysala" -> item.dynasty.contains("Hoysala", ignoreCase = true)
                else -> true
            }

            matchesSearch && matchesCategory
        }
    }

    Scaffold(
        topBar = {
            PrimaryTopBar(title = "Heritage Explorer")
        },
        containerColor = SageGreenSurface
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            // Heritage Explorer Hero Header
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 6.dp),
                shape = RoundedCornerShape(14.dp),
                colors = CardDefaults.cardColors(containerColor = StoneCardSurface),
                border = androidx.compose.foundation.BorderStroke(1.dp, StoneBorder)
            ) {
                Box(modifier = Modifier.fillMaxWidth()) {
                    com.shilora.app.ui.components.HeritageHeroBackground(
                        type = com.shilora.app.ui.components.HeritageHeroTextureType.ARCHAEOLOGICAL_MOTIF,
                        modifier = Modifier.matchParentSize()
                    )
                    Column(modifier = Modifier.padding(14.dp)) {
                        Text(
                            text = "Historical Inscription Catalog",
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = FontWeight.Bold,
                                color = NeutralBlack
                            )
                        )
                        Spacer(Modifier.height(2.dp))
                        Text(
                            text = "Discover landmark epigraphs across Kadamba, Chalukya, and Hoysala periods.",
                            style = MaterialTheme.typography.bodySmall.copy(color = NeutralDarkGrey)
                        )
                    }
                }
            }

            // Search Input Field
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 6.dp)
            ) {
                OutlinedTextField(
                    value = searchQuery,
                    onValueChange = { searchQuery = it },
                    placeholder = { Text("Search by inscription, place, or dynasty...", color = NeutralMediumGrey) },
                    leadingIcon = {
                        Icon(Icons.Default.Search, contentDescription = null, tint = SageGreenDark)
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(StoneCardSurface),
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = BurntAmber,
                        unfocusedBorderColor = StoneBorder,
                        focusedTextColor = NeutralBlack,
                        unfocusedTextColor = NeutralBlack
                    )
                )
            }

            // Category Filter Chips
            LazyRow(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp),
                contentPadding = PaddingValues(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(categories) { category ->
                    val isSelected = category == selectedCategory
                    FilterChip(
                        selected = isSelected,
                        onClick = { selectedCategory = category },
                        label = {
                            Text(
                                text = category,
                                style = MaterialTheme.typography.labelMedium.copy(
                                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                                    color = if (isSelected) NeutralWhite else NeutralBlack
                                )
                            )
                        },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = BurntAmber,
                            selectedLabelColor = NeutralWhite,
                            containerColor = StoneCardSurface,
                            labelColor = NeutralBlack
                        ),
                        border = FilterChipDefaults.filterChipBorder(
                            borderColor = if (isSelected) BurntAmber else StoneBorder,
                            selectedBorderColor = BurntAmber,
                            enabled = true,
                            selected = isSelected
                        ),
                        shape = RoundedCornerShape(10.dp)
                    )
                }
            }

            // Inscriptions Feed
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 16.dp),
                contentPadding = PaddingValues(top = 8.dp, bottom = 48.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                items(filteredItems, key = { it.id }) { item ->
                    HeritageItemCard(
                        item = item,
                        onClick = { onItemClick(item.id) }
                    )
                }
            }
        }
    }
}

@Composable
private fun HeritageItemCard(
    item: HeritageItem,
    onClick: () -> Unit
) {
    ShiloraCard(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(160.dp)
                .clip(RoundedCornerShape(12.dp))
                .background(ConcreteGreyLight)
        ) {
            AsyncImage(
                model = ImageRequest.Builder(LocalContext.current)
                    .data(item.imageUrl)
                    .crossfade(true)
                    .build(),
                contentDescription = item.title,
                contentScale = ContentScale.Crop,
                modifier = Modifier.fillMaxSize()
            )

            // Period Badge overlay
            Surface(
                modifier = Modifier
                    .padding(10.dp)
                    .align(Alignment.TopStart),
                shape = RoundedCornerShape(6.dp),
                color = SageGreenDark.copy(alpha = 0.9f)
            ) {
                Text(
                    text = item.century,
                    style = MaterialTheme.typography.labelSmall.copy(
                        color = NeutralWhite,
                        fontWeight = FontWeight.Bold
                    ),
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }
        }

        Spacer(Modifier.height(12.dp))

        Text(
            text = item.title,
            style = MaterialTheme.typography.titleMedium.copy(
                fontWeight = FontWeight.Bold,
                color = NeutralBlack
            )
        )

        Spacer(Modifier.height(4.dp))

        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Place,
                contentDescription = null,
                tint = BurntAmber,
                modifier = Modifier.size(16.dp)
            )
            Text(
                text = "${item.siteLocation} • ${item.dynasty}",
                style = MaterialTheme.typography.bodySmall.copy(color = NeutralMediumGrey)
            )
        }

        Spacer(Modifier.height(8.dp))

        Text(
            text = item.summary,
            style = MaterialTheme.typography.bodyMedium.copy(color = NeutralDarkGrey),
            maxLines = 2,
            overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis
        )
    }
}
